"""
LangGraph agent that manages HCP interaction logging via natural conversation.

Role of the agent:
The agent sits behind the "chat" tab of the Log Interaction Screen. It receives the
rep's free-text message, decides (via the LLM's tool-calling) whether it needs more
context (get_hcp_profile), should log a new interaction (log_interaction), amend one
that was just logged (edit_interaction), schedule a reminder (schedule_follow_up), or
recommend what to discuss next (suggest_next_best_action). It keeps the rep in a single
conversational surface instead of forcing them to fill separate form fields, while every
tool call still writes to the same relational tables the structured form uses -- so both
entry paths converge on identical data.
"""
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage, AIMessage

from app.agent.state import AgentState
from app.agent.tools import ALL_TOOLS
from app.agent.llm import get_llm

SYSTEM_PROMPT = """You are FieldMate, an AI assistant embedded in a pharma CRM's HCP
module. You help a field representative log and manage interactions with Healthcare
Professionals (HCPs) through conversation.

Guidelines:
- If the rep describes a visit/call/email in free text, call `log_interaction` to save it.
- If the rep wants to change something they just logged (e.g. "actually mark that as
  positive sentiment" or "add that I gave 2 samples"), call `edit_interaction` using the
  most recent interaction_id from the conversation.
- If you need HCP background before responding, call `get_hcp_profile`.
- If the rep asks to be reminded or to follow up, call `schedule_follow_up`.
- If the rep asks what to bring up next time, call `suggest_next_best_action`.
- Always confirm what you did in plain, concise language after a tool call.
- Never fabricate HCP data; only use what tools return.
"""


def build_graph():
    llm = get_llm(temperature=0.2)
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    def agent_node(state: AgentState):
        messages = state["messages"]
        if not any(isinstance(m, SystemMessage) for m in messages):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def should_continue(state: AgentState):
        last = state["messages"][-1]
        if getattr(last, "tool_calls", None):
            return "tools"
        return END

    tool_node = ToolNode(ALL_TOOLS)

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")

    return graph.compile()


_compiled_graph = None


def get_agent():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph
