import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from app.database import get_db
from app import models, schemas
from app.agent.graph import get_agent

router = APIRouter(prefix="/api/chat", tags=["Chat Agent"])


@router.post("/", response_model=schemas.ChatResponse)
def chat_with_agent(payload: schemas.ChatRequest, db: Session = Depends(get_db)):
    agent = get_agent()

    db.add(models.ChatMessage(
        session_id=payload.session_id, role="user", content=payload.message,
    ))
    db.commit()

    
    history = (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.session_id == payload.session_id)
        .order_by(models.ChatMessage.created_at.asc())
        .limit(20)
        .all()
    )

    lc_messages = []
    for m in history:
        if m.role == "user":
            content = m.content
            if payload.hcp_id and m.id == history[-1].id:
                content = f"[Active HCP id: {payload.hcp_id}] {content}"
            lc_messages.append(HumanMessage(content=content))
        elif m.role == "assistant":
            lc_messages.append(AIMessage(content=m.content))

    result = agent.invoke({
        "messages": lc_messages,
        "session_id": payload.session_id,
        "hcp_id": payload.hcp_id,
        "rep_name": payload.rep_name or "Field Rep",
        "tool_calls_log": [],
        "last_interaction_id": None,
    })

    out_messages = result["messages"]

    tool_calls = []
    last_interaction_id = None
    for i, msg in enumerate(out_messages):
        if isinstance(msg, AIMessage) and getattr(msg, "tool_calls", None):
            for tc in msg.tool_calls:
                # find the matching ToolMessage response that follows
                tool_output = None
                for later in out_messages[i + 1:]:
                    if isinstance(later, ToolMessage) and later.tool_call_id == tc["id"]:
                        tool_output = later.content
                        break
                tool_calls.append(schemas.ToolCallLog(
                    tool_name=tc["name"], tool_input=tc["args"], tool_output=tool_output,
                ))
                if tc["name"] in ("log_interaction", "edit_interaction") and tool_output:
                    try:
                        parsed = json.loads(tool_output)
                        if "interaction_id" in parsed:
                            last_interaction_id = parsed["interaction_id"]
                    except json.JSONDecodeError:
                        pass

    final_ai_messages = [m for m in out_messages if isinstance(m, AIMessage) and m.content]
    reply_text = final_ai_messages[-1].content if final_ai_messages else "Done."

    db.add(models.ChatMessage(
        session_id=payload.session_id, role="assistant", content=reply_text,
    ))
    db.commit()

    interaction_out = None
    if last_interaction_id:
        interaction = db.query(models.Interaction).filter(models.Interaction.id == last_interaction_id).first()
        if interaction:
            interaction_out = schemas.InteractionOut.model_validate(interaction)

    return schemas.ChatResponse(
        session_id=payload.session_id,
        reply=reply_text,
        tool_calls=tool_calls,
        interaction=interaction_out,
    )
