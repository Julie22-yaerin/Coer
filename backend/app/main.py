import asyncio
import json
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, List, Optional, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from app.config import settings
from app.db.session import init_db, get_session
from app.db.repository import Repository
from app.models.schema import (
    FounderProfile,
    MeetingSession,
    TranscriptUtterance,
    PsychometricReport,
    RealtimeSuggestionEvent,
    CreateSessionRequest,
    CreateFounderProfileRequest,
)
from app.llm.copilot_stream import CopilotStreamEngine
from app.analysis.synthesizer import PsychometricSynthesizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("coer.engine")

# ------------------------------------------------------------------------------
# Active Session State & Connection Manager
# ------------------------------------------------------------------------------

class SessionManager:
    def __init__(self):
        self.active_websockets: Set[WebSocket] = set()
        self.current_session_id: Optional[str] = None
        self.rolling_context: List[str] = []
        self.last_candidate_speech_time: float = time.time()
        self.copilot_engine = CopilotStreamEngine()
        self.synthesizer = PsychometricSynthesizer()
        self._silence_monitor_task: Optional[asyncio.Task] = None

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_websockets.add(websocket)
        logger.info(f"WebSocket client connected. Total connections: {len(self.active_websockets)}")

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_websockets.discard(websocket)
        logger.info(f"WebSocket client disconnected. Total connections: {len(self.active_websockets)}")

    async def broadcast(self, message: Dict) -> None:
        disconnected = set()
        payload = json.dumps(message)
        for ws in self.active_websockets:
            try:
                await ws.send_text(payload)
            except Exception:
                disconnected.add(ws)
        for ws in disconnected:
            self.active_websockets.discard(ws)

    def start_session(self, session_id: str) -> None:
        self.current_session_id = session_id
        self.rolling_context = []
        self.last_candidate_speech_time = time.time()
        if not self._silence_monitor_task or self._silence_monitor_task.done():
            self._silence_monitor_task = asyncio.create_task(self._monitor_silence())

    def end_session(self) -> None:
        self.current_session_id = None
        if self._silence_monitor_task:
            self._silence_monitor_task.cancel()

    def add_utterance_context(self, speaker: str, text: str) -> None:
        prefix = "Candidate" if speaker == "candidate" else "Founder"
        self.rolling_context.append(f"{prefix}: {text}")
        if len(self.rolling_context) > settings.MAX_CONTEXT_UTTERANCES:
            self.rolling_context.pop(0)

        if speaker == "candidate":
            self.last_candidate_speech_time = time.time()

    async def trigger_suggestion(self, reason: str = "manual_hotkey") -> None:
        if not self.rolling_context:
            return
        questions, tip, latency_ms = await self.copilot_engine.generate_suggestions(
            self.rolling_context, trigger_reason=reason
        )
        event = RealtimeSuggestionEvent(
            event_type="suggestion",
            timestamp_ms=int(time.time() * 1000),
            trigger_reason=reason,
            last_context=list(self.rolling_context),
            suggested_questions=questions,
            tactical_tip=tip,
            latency_ms=latency_ms,
        )
        await self.broadcast(event.model_dump())

    async def _monitor_silence(self) -> None:
        """Background task checking if candidate has paused > 1.5s"""
        while True:
            await asyncio.sleep(0.5)
            if self.current_session_id and self.rolling_context:
                elapsed = time.time() - self.last_candidate_speech_time
                if elapsed >= settings.SILENCE_THRESHOLD_SEC:
                    # Reset timer so we don't spam suggestions repeatedly while silent
                    self.last_candidate_speech_time = time.time() + 999999
                    await self.trigger_suggestion(reason="silence_timeout")

session_manager = SessionManager()

# ------------------------------------------------------------------------------
# Lifespan
# ------------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Coer Database tables...")
    init_db()
    logger.info("Coer Database initialized successfully.")
    yield
    logger.info("Shutting down Coer Engine...")
    session_manager.end_session()

app = FastAPI(
    title="Coer AI Engine",
    description="Undetectable Desktop AI Co-founder Copilot & Matching Engine",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------------------
# REST Endpoints
# ------------------------------------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "app": "Coer Engine",
        "version": "0.1.0",
        "timestamp": datetime.utcnow().isoformat(),
        "active_session": session_manager.current_session_id,
    }

@app.post("/api/founder/profile", response_model=FounderProfile)
def save_founder_profile(req: CreateFounderProfileRequest, session: Session = Depends(get_session)):
    repo = Repository(session)
    profile = FounderProfile(
        name=req.name,
        role=req.role,
        vision_statement=req.vision_statement,
        ocean_traits=req.ocean_traits,
        key_values=req.key_values,
    )
    return repo.create_or_update_founder_profile(profile)

@app.get("/api/founder/profile", response_model=Optional[FounderProfile])
def get_founder_profile(session: Session = Depends(get_session)):
    repo = Repository(session)
    return repo.get_founder_profile()

@app.post("/api/sessions", response_model=MeetingSession)
def create_session(req: CreateSessionRequest, session: Session = Depends(get_session)):
    repo = Repository(session)
    new_session = MeetingSession(
        candidate_name=req.candidate_name,
        target_role=req.target_role,
        status="IN_PROGRESS",
    )
    saved = repo.create_session(new_session)
    session_manager.start_session(saved.id)
    return saved

@app.get("/api/sessions", response_model=List[MeetingSession])
def list_sessions(limit: int = Query(50), session: Session = Depends(get_session)):
    repo = Repository(session)
    return repo.list_sessions(limit=limit)

@app.get("/api/sessions/{session_id}", response_model=MeetingSession)
def get_session_details(session_id: str, session: Session = Depends(get_session)):
    repo = Repository(session)
    db_session = repo.get_session(session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session

@app.post("/api/sessions/{session_id}/end", response_model=PsychometricReport)
async def end_session(session_id: str, session: Session = Depends(get_session)):
    repo = Repository(session)
    db_session = repo.get_session(session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    repo.update_session_status(session_id, status="COMPLETED", ended_at=datetime.utcnow())
    session_manager.end_session()

    # Retrieve all utterances for deep synthesis
    utterances = repo.get_session_utterances(session_id)
    founder = repo.get_founder_profile()

    # Generate psychometric report
    report = await session_manager.synthesizer.synthesize(
        session_id=session_id, utterances=utterances, founder=founder
    )
    saved_report = repo.save_report(report)

    # Broadcast completion report to frontend
    await session_manager.broadcast({
        "event_type": "report",
        "session_id": session_id,
        "report": saved_report.model_dump(),
    })

    return saved_report

@app.get("/api/sessions/{session_id}/report", response_model=PsychometricReport)
def get_session_report(session_id: str, session: Session = Depends(get_session)):
    repo = Repository(session)
    report = repo.get_report_by_session(session_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not generated yet for this session")
    return report

# ------------------------------------------------------------------------------
# Real-Time WebSocket Endpoint
# ------------------------------------------------------------------------------

@app.websocket("/ws/copilot")
async def copilot_websocket_endpoint(websocket: WebSocket, session: Session = Depends(get_session)):
    await session_manager.connect(websocket)
    repo = Repository(session)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                action = msg.get("action")

                if action == "start_session":
                    s_id = msg.get("session_id")
                    if s_id:
                        session_manager.start_session(s_id)
                        await websocket.send_text(json.dumps({
                            "event_type": "status",
                            "status": "session_started",
                            "session_id": s_id
                        }))

                elif action == "utterance":
                    s_id = msg.get("session_id") or session_manager.current_session_id
                    speaker = msg.get("speaker", "candidate")
                    text = msg.get("text", "").strip()
                    if text and s_id:
                        start_time_ms = msg.get("start_time_ms", 0)
                        end_time_ms = msg.get("end_time_ms", 0)
                        confidence = msg.get("confidence", 1.0)

                        utterance = TranscriptUtterance(
                            session_id=s_id,
                            speaker=speaker,
                            text=text,
                            start_time_ms=start_time_ms,
                            end_time_ms=end_time_ms,
                            confidence=confidence,
                        )
                        repo.add_utterance(utterance)
                        session_manager.add_utterance_context(speaker, text)

                        # Broadcast transcript to UI
                        await session_manager.broadcast({
                            "event_type": "transcript",
                            "session_id": s_id,
                            "speaker": speaker,
                            "text": text,
                            "start_time_ms": start_time_ms,
                            "end_time_ms": end_time_ms,
                        })

                elif action == "request_suggestion":
                    # Manually triggered by Ctrl+Enter hotkey
                    await session_manager.trigger_suggestion(reason="manual_hotkey")

                elif action == "end_session":
                    s_id = msg.get("session_id") or session_manager.current_session_id
                    if s_id:
                        session_manager.end_session()
                        await websocket.send_text(json.dumps({
                            "event_type": "status",
                            "status": "session_ended",
                            "session_id": s_id
                        }))

            except json.JSONDecodeError:
                logger.error("Failed to decode JSON from websocket client.")
            except Exception as e:
                logger.error(f"Error handling websocket action: {e}")

    except WebSocketDisconnect:
        session_manager.disconnect(websocket)
