"""
LangGraph agent tools for the HCP Log Interaction module.

Five tools are exposed to the agent:
  1. log_interaction         - captures a free-text interaction, uses the LLM to
                                summarize + extract entities, and persists a record.
  2. edit_interaction        - modifies a previously logged interaction.
  3. get_hcp_profile         - fetches HCP details + recent interaction history (context tool).
  4. schedule_follow_up      - creates a follow-up reminder tied to an interaction.
  5. suggest_next_best_action- LLM-generated talking points / product suggestions
                                for the rep's next visit, grounded in interaction history.
"""
import json
from datetime import datetime, timedelta
from typing import Optional, List

from langchain_core.tools import tool

from app.database import SessionLocal
from app import models
from app.agent.llm import get_llm, get_fallback_llm

EXTRACTION_SYSTEM_PROMPT = """You are a life-science CRM assistant. Given a field
representative's free-text note about an interaction with a Healthcare Professional (HCP),
extract structured data. Respond with STRICT JSON ONLY, no markdown, matching this schema:

{
  "summary": "one or two sentence neutral summary",
  "interaction_type": "visit|call|email|event|sample_drop",
  "topics_discussed": ["..."],
  "products_discussed": ["..."],
  "samples_provided": ["..."],
  "sentiment": "positive|neutral|negative",
  "follow_up_required": true|false,
  "follow_up_notes": "short note or empty string"
}"""


def _extract_entities(raw_text: str) -> dict:
    llm = get_llm(temperature=0.1)
    messages = [
        {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
        {"role": "user", "content": raw_text},
    ]
    result = llm.invoke(messages)
    content = result.content.strip()
    if content.startswith("```"):
        content = content.strip("`")
        content = content.replace("json\n", "", 1) if content.startswith("json\n") else content
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        data = {
            "summary": raw_text[:200],
            "interaction_type": "visit",
            "topics_discussed": [],
            "products_discussed": [],
            "samples_provided": [],
            "sentiment": "neutral",
            "follow_up_required": False,
            "follow_up_notes": "",
        }
    return data


@tool
def log_interaction(hcp_id: str, rep_name: str, raw_text: str, channel: str = "chat") -> str:
    """Log a new HCP interaction from free text. Uses the LLM to summarize the note,
    extract discussed topics/products/samples, sentiment, and whether a follow-up is
    required. Returns a JSON string with the created interaction's id and summary."""
    db = SessionLocal()
    try:
        hcp = db.query(models.HCP).filter(models.HCP.id == hcp_id).first()
        if not hcp:
            return json.dumps({"error": f"HCP with id {hcp_id} not found"})

        extracted = _extract_entities(raw_text)

        interaction = models.Interaction(
            hcp_id=hcp_id,
            rep_name=rep_name,
            channel=channel,
            interaction_type=extracted.get("interaction_type", "visit"),
            raw_text=raw_text,
            summary=extracted.get("summary"),
            topics_discussed=extracted.get("topics_discussed", []),
            products_discussed=extracted.get("products_discussed", []),
            samples_provided=extracted.get("samples_provided", []),
            sentiment=extracted.get("sentiment", "neutral"),
            follow_up_required=extracted.get("follow_up_required", False),
            follow_up_notes=extracted.get("follow_up_notes", ""),
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)

        return json.dumps({
            "interaction_id": interaction.id,
            "hcp_name": f"{hcp.first_name} {hcp.last_name}",
            "summary": interaction.summary,
            "topics_discussed": interaction.topics_discussed,
            "products_discussed": interaction.products_discussed,
            "sentiment": interaction.sentiment,
            "follow_up_required": interaction.follow_up_required,
        })
    finally:
        db.close()


@tool
def edit_interaction(interaction_id: str, updates_json: str) -> str:
    """Edit a previously logged interaction. `updates_json` must be a JSON string of
    fields to change, e.g. {"summary": "...", "sentiment": "positive", "follow_up_required": true}.
    Returns the updated interaction as JSON."""
    db = SessionLocal()
    try:
        interaction = db.query(models.Interaction).filter(models.Interaction.id == interaction_id).first()
        if not interaction:
            return json.dumps({"error": f"Interaction {interaction_id} not found"})
        try:
            updates = json.loads(updates_json)
        except json.JSONDecodeError:
            return json.dumps({"error": "updates_json was not valid JSON"})

        allowed = {
            "summary", "interaction_type", "topics_discussed", "products_discussed",
            "samples_provided", "sentiment", "follow_up_required", "follow_up_notes", "rep_name",
        }
        for key, value in updates.items():
            if key in allowed:
                setattr(interaction, key, value)
        interaction.is_edited = True
        db.commit()
        db.refresh(interaction)

        return json.dumps({
            "interaction_id": interaction.id,
            "summary": interaction.summary,
            "sentiment": interaction.sentiment,
            "topics_discussed": interaction.topics_discussed,
            "products_discussed": interaction.products_discussed,
            "follow_up_required": interaction.follow_up_required,
            "is_edited": interaction.is_edited,
        })
    finally:
        db.close()


@tool
def get_hcp_profile(hcp_id: str, history_limit: int = 5) -> str:
    """Fetch an HCP's profile plus their most recent interaction history, to give
    the agent context before logging a new note or suggesting next steps."""
    db = SessionLocal()
    try:
        hcp = db.query(models.HCP).filter(models.HCP.id == hcp_id).first()
        if not hcp:
            return json.dumps({"error": f"HCP {hcp_id} not found"})
        history = (
            db.query(models.Interaction)
            .filter(models.Interaction.hcp_id == hcp_id)
            .order_by(models.Interaction.interaction_date.desc())
            .limit(history_limit)
            .all()
        )
        return json.dumps({
            "hcp": {
                "id": hcp.id,
                "name": f"{hcp.first_name} {hcp.last_name}",
                "specialty": hcp.specialty,
                "institution": hcp.institution,
                "preferred_products": hcp.preferred_products,
            },
            "recent_interactions": [
                {
                    "id": i.id,
                    "date": i.interaction_date.isoformat(),
                    "summary": i.summary,
                    "products_discussed": i.products_discussed,
                    "sentiment": i.sentiment,
                }
                for i in history
            ],
        })
    finally:
        db.close()


@tool
def schedule_follow_up(hcp_id: str, interaction_id: str, days_from_now: int, notes: str = "") -> str:
    """Schedule a follow-up task for an HCP tied to a specific interaction, due in
    `days_from_now` days. Returns the created follow-up as JSON."""
    db = SessionLocal()
    try:
        interaction = db.query(models.Interaction).filter(models.Interaction.id == interaction_id).first()
        if not interaction:
            return json.dumps({"error": f"Interaction {interaction_id} not found"})
        due = datetime.utcnow() + timedelta(days=days_from_now)
        follow_up = models.FollowUp(
            interaction_id=interaction_id,
            hcp_id=hcp_id,
            due_date=due,
            notes=notes,
            status="pending",
        )
        db.add(follow_up)
        interaction.follow_up_required = True
        if notes:
            interaction.follow_up_notes = notes
        db.commit()
        db.refresh(follow_up)
        return json.dumps({
            "follow_up_id": follow_up.id,
            "due_date": follow_up.due_date.isoformat(),
            "notes": follow_up.notes,
            "status": follow_up.status,
        })
    finally:
        db.close()


@tool
def suggest_next_best_action(hcp_id: str) -> str:
    """Use the larger LLM (llama-3.3-70b-versatile) to suggest talking points and
    products for the rep's next interaction with this HCP, grounded in their
    interaction history and preferences."""
    db = SessionLocal()
    try:
        hcp = db.query(models.HCP).filter(models.HCP.id == hcp_id).first()
        if not hcp:
            return json.dumps({"error": f"HCP {hcp_id} not found"})
        history = (
            db.query(models.Interaction)
            .filter(models.Interaction.hcp_id == hcp_id)
            .order_by(models.Interaction.interaction_date.desc())
            .limit(5)
            .all()
        )
        history_text = "\n".join(
            f"- {i.interaction_date.date()}: {i.summary} "
            f"(products: {i.products_discussed}, sentiment: {i.sentiment})"
            for i in history
        ) or "No prior interactions logged."

        llm = get_fallback_llm(temperature=0.4)
        prompt = (
            f"HCP: Dr. {hcp.first_name} {hcp.last_name}, {hcp.specialty}, {hcp.institution}.\n"
            f"Preferred products: {hcp.preferred_products}.\n"
            f"Recent interaction history:\n{history_text}\n\n"
            "Suggest 3 concise, specific talking points and 1-2 relevant products for the "
            "rep's next visit. Respond in 4-6 short bullet points, no preamble."
        )
        result = llm.invoke([{"role": "user", "content": prompt}])
        return json.dumps({"hcp_id": hcp_id, "suggestions": result.content.strip()})
    finally:
        db.close()


ALL_TOOLS = [
    log_interaction,
    edit_interaction,
    get_hcp_profile,
    schedule_follow_up,
    suggest_next_best_action,
]
