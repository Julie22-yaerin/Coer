from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel, Field as PydanticField
import uuid

# ==============================================================================
# SQLModel Database Schemas (Persistence)
# ==============================================================================

class FounderProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    role: str  # e.g., "Technical CEO", "Product Lead"
    vision_statement: str
    ocean_traits: Dict[str, float] = Field(default_factory=dict, sa_column_kwargs={"type_": "JSON"})
    key_values: List[str] = Field(default_factory=list, sa_column_kwargs={"type_": "JSON"})
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MeetingSession(SQLModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    candidate_name: str
    target_role: str
    status: str = Field(default="IN_PROGRESS")  # IN_PROGRESS, COMPLETED, FAILED
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    total_duration_sec: Optional[int] = None
    audio_path: Optional[str] = None
    
    # Relationships
    utterances: List["TranscriptUtterance"] = Relationship(back_populates="session")
    report: Optional["PsychometricReport"] = Relationship(back_populates="session")

class TranscriptUtterance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(foreign_key="meetingsession.id")
    speaker: str  # "founder" | "candidate"
    text: str
    start_time_ms: int
    end_time_ms: int
    confidence: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    session: Optional[MeetingSession] = Relationship(back_populates="utterances")

class PsychometricReport(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(foreign_key="meetingsession.id", unique=True)
    
    # Quantitative Scores (0 - 100)
    ocean_openness: float
    ocean_conscientiousness: float
    ocean_extraversion: float
    ocean_agreeableness: float
    ocean_neuroticism: float
    complementarity_index: float
    
    # Structured Insights
    motivation_drivers: List[str] = Field(default_factory=list, sa_column_kwargs={"type_": "JSON"})
    red_flags: List[str] = Field(default_factory=list, sa_column_kwargs={"type_": "JSON"})
    strengths: List[str] = Field(default_factory=list, sa_column_kwargs={"type_": "JSON"})
    evidence_citations: List[Dict[str, Any]] = Field(default_factory=list, sa_column_kwargs={"type_": "JSON"})
    full_markdown_report: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    session: Optional[MeetingSession] = Relationship(back_populates="report")


# ==============================================================================
# Real-Time WebSocket Message Contracts (Pydantic v2)
# ==============================================================================

class RealtimeSuggestionEvent(BaseModel):
    event_type: str = "suggestion"
    timestamp_ms: int
    trigger_reason: str  # "silence_timeout" | "manual_hotkey"
    last_context: List[str]
    suggested_questions: List[str]
    tactical_tip: Optional[str] = None
    latency_ms: float

class RealtimeTranscriptEvent(BaseModel):
    event_type: str = "transcript"
    session_id: str
    speaker: str  # "founder" | "candidate"
    text: str
    is_final: bool = True
    start_time_ms: int
    end_time_ms: int
    confidence: float = 1.0

class SessionStatusEvent(BaseModel):
    event_type: str = "status"
    session_id: str
    status: str
    message: Optional[str] = None

# ==============================================================================
# REST API DTOs
# ==============================================================================

class CreateSessionRequest(BaseModel):
    candidate_name: str
    target_role: str

class EndSessionRequest(BaseModel):
    session_id: str

class CreateFounderProfileRequest(BaseModel):
    name: str
    role: str
    vision_statement: str
    ocean_traits: Dict[str, float] = PydanticField(default_factory=dict)
    key_values: List[str] = PydanticField(default_factory=list)
