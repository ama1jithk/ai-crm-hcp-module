from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, ConfigDict


class HCPBase(BaseModel):
    first_name: str
    last_name: str
    specialty: Optional[str] = None
    institution: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    territory: Optional[str] = None
    preferred_products: Optional[List[str]] = []


class HCPCreate(HCPBase):
    pass


class HCPOut(HCPBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime


class InteractionBase(BaseModel):
    hcp_id: str
    rep_name: Optional[str] = "Field Rep"
    channel: Optional[str] = "form"
    interaction_type: Optional[str] = "visit"
    raw_text: Optional[str] = None
    summary: Optional[str] = None
    topics_discussed: Optional[List[str]] = []
    products_discussed: Optional[List[str]] = []
    sentiment: Optional[str] = None
    samples_provided: Optional[List[str]] = []
    follow_up_required: Optional[bool] = False
    follow_up_notes: Optional[str] = None


class InteractionCreate(InteractionBase):
    pass


class InteractionUpdate(BaseModel):
    rep_name: Optional[str] = None
    interaction_type: Optional[str] = None
    summary: Optional[str] = None
    topics_discussed: Optional[List[str]] = None
    products_discussed: Optional[List[str]] = None
    sentiment: Optional[str] = None
    samples_provided: Optional[List[str]] = None
    follow_up_required: Optional[bool] = None
    follow_up_notes: Optional[str] = None


class InteractionOut(InteractionBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    interaction_date: datetime
    is_edited: bool
    created_at: datetime
    updated_at: datetime


class ChatRequest(BaseModel):
    session_id: str
    message: str
    hcp_id: Optional[str] = None
    rep_name: Optional[str] = "Field Rep"


class ToolCallLog(BaseModel):
    tool_name: str
    tool_input: Any
    tool_output: Any


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    tool_calls: List[ToolCallLog] = []
    interaction: Optional[InteractionOut] = None
