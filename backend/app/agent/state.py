from typing import TypedDict, Annotated, List, Optional, Any
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    session_id: str
    hcp_id: Optional[str]
    rep_name: str
    tool_calls_log: List[dict]
    last_interaction_id: Optional[str]
