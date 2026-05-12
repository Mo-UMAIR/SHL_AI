from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    messages: List[Dict[str, str]]
    intent: Optional[str]
    retrieved_docs: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    reply: str
    end_of_conversation: bool
