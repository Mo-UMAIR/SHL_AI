from fastapi import APIRouter, HTTPException
from backend.models.schemas import ChatRequest, ChatResponse, Recommendation
from backend.agents.graph import agent_graph

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # Convert Pydantic models to dicts for LangGraph
        messages_list = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        initial_state = {
            "messages": messages_list,
            "intent": None,
            "retrieved_docs": [],
            "recommendations": [],
            "reply": "",
            "end_of_conversation": False
        }
        
        # Invoke the LangGraph agent
        final_state = agent_graph.invoke(initial_state)
        
        # Convert dictionary recommendations back to Pydantic objects or just let FastAPI handle it
        # Actually, FastAPI handles dicts just fine when matching the response_model schema
        
        return ChatResponse(
            reply=final_state.get("reply", ""),
            recommendations=[Recommendation(**r) for r in final_state.get("recommendations", [])],
            end_of_conversation=final_state.get("end_of_conversation", False)
        )
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        # According to requirements, schema must never break, even on error
        # So we return a safe fallback
        return ChatResponse(
            reply="An internal error occurred. Please try again.",
            recommendations=[],
            end_of_conversation=False
        )
