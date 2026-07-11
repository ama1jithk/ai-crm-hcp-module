import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class InteractionChannel(str, enum.Enum):
    FORM = "form"
    CHAT = "chat"


class InteractionType(str, enum.Enum):
    VISIT = "visit"
    CALL = "call"
    EMAIL = "email"
    EVENT = "event"
    SAMPLE_DROP = "sample_drop"


class HCP(Base):
    __tablename__ = "hcps"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    specialty = Column(String(150), nullable=True)
    institution = Column(String(200), nullable=True)
    email = Column(String(150), nullable=True)
    phone = Column(String(50), nullable=True)
    territory = Column(String(100), nullable=True)
    preferred_products = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    interactions = relationship("Interaction", back_populates="hcp", cascade="all, delete-orphan")


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    hcp_id = Column(String(36), ForeignKey("hcps.id"), nullable=False)
    rep_name = Column(String(150), nullable=False, default="Field Rep")
    channel = Column(Enum(InteractionChannel), default=InteractionChannel.FORM)
    interaction_type = Column(Enum(InteractionType), default=InteractionType.VISIT)
    interaction_date = Column(DateTime, default=datetime.utcnow)
    raw_text = Column(Text, nullable=True)          # original free text (chat mode)
    summary = Column(Text, nullable=True)            # LLM generated summary
    topics_discussed = Column(JSON, default=list)    # entity extraction output
    products_discussed = Column(JSON, default=list)
    sentiment = Column(String(50), nullable=True)    # positive / neutral / negative
    samples_provided = Column(JSON, default=list)
    follow_up_required = Column(Boolean, default=False)
    follow_up_notes = Column(Text, nullable=True)
    attachments = Column(JSON, default=list)
    is_edited = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    hcp = relationship("HCP", back_populates="interactions")


class FollowUp(Base):
    __tablename__ = "follow_ups"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    interaction_id = Column(String(36), ForeignKey("interactions.id"), nullable=False)
    hcp_id = Column(String(36), ForeignKey("hcps.id"), nullable=False)
    due_date = Column(DateTime, nullable=False)
    notes = Column(Text, nullable=True)
    status = Column(String(50), default="pending")  # pending / done / cancelled
    created_at = Column(DateTime, default=datetime.utcnow)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    session_id = Column(String(36), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user / assistant / tool
    content = Column(Text, nullable=False)
    tool_name = Column(String(100), nullable=True)
    tool_payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
