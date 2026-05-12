import os
import json
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from backend.agents.state import AgentState
from backend.prompts.templates import INTENT_CLASSIFICATION_PROMPT, RESPONSE_GENERATION_PROMPT
from backend.vectorstore.faiss_store import FAISSRetriever

# Initialize LLM
# Using Gemini 1.5 Flash as requested (via google-genai)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.0)

# We expect the retriever to be initialized externally or here as a singleton
# Assuming the FastAPI app will initialize it and pass it or we use a global
# For simplicity, we can load it lazily
retriever = None

def get_retriever():
    global retriever
    if retriever is None:
        catalog_path = os.path.join(os.path.dirname(__file__), "..", "data", "catalog.json")
        retriever = FAISSRetriever(catalog_path=catalog_path)
    return retriever

def format_history(messages: List[Dict[str, str]]) -> str:
    return "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in messages])

def classify_intent_node(state: AgentState) -> AgentState:
    history_str = format_history(state["messages"])
    prompt = PromptTemplate.from_template(INTENT_CLASSIFICATION_PROMPT)
    chain = prompt | llm
    result = chain.invoke({"history": history_str})
    
    intent = result.content.strip().upper()
    # Fallback cleanup
    for valid_intent in ["CLARIFY", "RECOMMEND", "REFINE", "COMPARE", "REFUSE"]:
        if valid_intent in intent:
            intent = valid_intent
            break
            
    return {"intent": intent}

def retrieve_node(state: AgentState) -> AgentState:
    intent = state.get("intent", "")
    if intent in ["RECOMMEND", "REFINE", "COMPARE"]:
        # Extract query from the last user message
        user_messages = [m["content"] for m in state["messages"] if m["role"] == "user"]
        last_query = user_messages[-1] if user_messages else ""
        
        # We can also pass the whole history to LLM to extract a better search query
        # But for speed, we use the last message + previous context if short
        search_query = " ".join(user_messages[-2:]) if len(user_messages) >= 2 else last_query
        
        r = get_retriever()
        docs = r.search(query=search_query, top_k=10)
        return {"retrieved_docs": docs}
    
    return {"retrieved_docs": []}

def generate_response_node(state: AgentState) -> AgentState:
    intent = state.get("intent", "CLARIFY")
    docs = state.get("retrieved_docs", [])
    history_str = format_history(state["messages"])
    
    context_str = ""
    if docs:
        for i, doc in enumerate(docs):
            context_str += f"{i+1}. Name: {doc.get('name')} | URL: {doc.get('url')} | Type: {doc.get('test_type')} | Desc: {doc.get('description')}\n"
    
    # We ask the LLM to output JSON to get the reply and end_of_conversation flag
    # We use a modified prompt
    json_prompt = RESPONSE_GENERATION_PROMPT + "\n\nRespond EXACTLY with a JSON object containing two keys: 'reply' (string) and 'end_of_conversation' (boolean). Do NOT include markdown blocks."
    
    prompt = PromptTemplate.from_template(json_prompt)
    
    # We use a lower temperature for consistent JSON
    json_llm = llm.bind(response_format={"type": "json_object"})
    # Some older LangChain wrappers for Gemini might not support response_format nicely,
    # so we will parse it manually just in case.
    chain = prompt | llm
    
    try:
        result = chain.invoke({
            "intent": intent,
            "context": context_str,
            "history": history_str
        })
        
        # Clean up markdown JSON block if present
        content = result.content.strip()
        if content.startswith("```json"):
            content = content.replace("```json", "", 1).strip()
        if content.endswith("```"):
            content = content[:-3].strip()
            
        parsed = json.loads(content)
        reply = parsed.get("reply", "I'm sorry, I couldn't process that.")
        end_of_conversation = parsed.get("end_of_conversation", False)
    except Exception as e:
        print(f"Error parsing LLM response: {e}")
        reply = "I understand. Let me help you with that."
        end_of_conversation = False

    # Build recommendations list
    recommendations = []
    if intent in ["RECOMMEND", "REFINE"]:
        # Only include top 1-10 recommendations
        # If intent is to drop something, we should actually filter it based on LLM,
        # but the simplest way is to let the FAISS retriever handle it or just return the FAISS results.
        # Reranking based on constraints could be done here.
        for doc in docs[:10]: # Max 10
            recommendations.append({
                "name": doc.get("name", ""),
                "url": doc.get("url", ""),
                "test_type": doc.get("test_type", "")
            })
            
    return {
        "reply": reply,
        "recommendations": recommendations,
        "end_of_conversation": end_of_conversation
    }

# Build the graph
workflow = StateGraph(AgentState)

workflow.add_node("classify_intent", classify_intent_node)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("generate_response", generate_response_node)

workflow.set_entry_point("classify_intent")
workflow.add_edge("classify_intent", "retrieve")
workflow.add_edge("retrieve", "generate_response")
workflow.add_edge("generate_response", END)

agent_graph = workflow.compile()
