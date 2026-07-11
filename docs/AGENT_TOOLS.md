# LangGraph Agent & Tools — HCP Log Interaction Screen

## Role of the agent
The LangGraph agent (`backend/app/agent/graph.py`) sits behind the conversational tab
of the Log Interaction Screen. Instead of the rep filling in discrete form fields, they
describe the visit/call/email in plain language. The agent decides — through Groq's
`gemma2-9b-it` tool-calling — which of five tools to invoke, executes them against the
same MySQL/Postgres tables the structured form writes to, and replies conversationally
confirming what was recorded. This keeps both entry paths (form and chat) converging on
identical, structured CRM data.

The graph is a single-node ReAct-style loop: `agent -> tools -> agent -> ... -> END`,
built with `langgraph.prebuilt.ToolNode` and `StateGraph`. State (`AgentState`) tracks
the message history, active session, HCP id, and rep name across turns.

## The five tools

| Tool | Purpose |
|---|---|
| `log_interaction` | **(required)** Takes the rep's free text, calls the LLM with a strict JSON-extraction prompt to produce a summary, interaction type, topics/products/samples discussed, sentiment, and follow-up flag, then persists an `Interaction` row. |
| `edit_interaction` | **(required)** Accepts an `interaction_id` and a JSON patch of fields (e.g. `{"sentiment": "positive"}`), applies it, and marks the record `is_edited=True`. |
| `get_hcp_profile` | Fetches an HCP's profile and last N interactions, used by the agent to ground its responses in real history before logging or suggesting anything. |
| `schedule_follow_up` | Creates a `FollowUp` row due N days from now, tied to an interaction, and flips `follow_up_required` on that interaction. |
| `suggest_next_best_action` | Uses the larger `llama-3.3-70b-versatile` model to turn recent interaction history into 3–5 concrete talking points/products for the next visit. |

### `log_interaction` in detail
1. Rep sends free text, e.g. *"Met Dr. Rao, discussed CardioGuard XR dosing, she was
   positive, left 2 samples."*
2. The agent calls `log_interaction(hcp_id, rep_name, raw_text)`.
3. Inside the tool, `_extract_entities()` sends the text to Groq with a system prompt
   demanding strict JSON output (summary, interaction_type, topics_discussed,
   products_discussed, samples_provided, sentiment, follow_up_required, follow_up_notes).
4. The parsed JSON is used to construct and commit an `Interaction` SQLAlchemy row.
5. The tool returns a compact JSON confirmation, which the agent turns into a natural
   confirmation message back to the rep.

### `edit_interaction` in detail
The rep can immediately say *"actually change the sentiment to positive"* or *"add
that I also gave a starter kit"*. The agent resolves the target `interaction_id` from
context (the most recent one created in the conversation), builds a JSON patch, and
calls `edit_interaction`. Only an allow-listed set of fields can be updated; the row is
flagged `is_edited=True` so the UI can visually mark amended entries.
