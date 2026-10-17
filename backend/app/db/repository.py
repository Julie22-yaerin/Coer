from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from app.models.schema import (
    FounderProfile,
    MeetingSession,
    TranscriptUtterance,
    PsychometricReport,
)

class Repository:
    def __init__(self, session: Session):
        self.session = session

    # Founder Profile
    def get_founder_profile(self) -> Optional[FounderProfile]:
        statement = select(FounderProfile).order_by(FounderProfile.created_at.desc())
        return self.session.exec(statement).first()

    def create_or_update_founder_profile(self, profile: FounderProfile) -> FounderProfile:
        self.session.add(profile)
        self.session.commit()
        self.session.refresh(profile)
        return profile

    # Meeting Session
    def create_session(self, session: MeetingSession) -> MeetingSession:
        self.session.add(session)
        self.session.commit()
        self.session.refresh(session)
        return session

    def get_session(self, session_id: str) -> Optional[MeetingSession]:
        return self.session.get(MeetingSession, session_id)

    def list_sessions(self, limit: int = 50) -> List[MeetingSession]:
        statement = select(MeetingSession).order_by(MeetingSession.started_at.desc()).limit(limit)
        return list(self.session.exec(statement).all())

    def update_session_status(
        self, session_id: str, status: str, ended_at: Optional[datetime] = None
    ) -> Optional[MeetingSession]:
        db_session = self.get_session(session_id)
        if db_session:
            db_session.status = status
            if ended_at:
                db_session.ended_at = ended_at
                if db_session.started_at:
                    db_session.total_duration_sec = int((ended_at - db_session.started_at).total_seconds())
            self.session.add(db_session)
            self.session.commit()
            self.session.refresh(db_session)
        return db_session

    # Utterances
    def add_utterance(self, utterance: TranscriptUtterance) -> TranscriptUtterance:
        self.session.add(utterance)
        self.session.commit()
        self.session.refresh(utterance)
        return utterance

    def get_session_utterances(self, session_id: str) -> List[TranscriptUtterance]:
        statement = (
            select(TranscriptUtterance)
            .where(TranscriptUtterance.session_id == session_id)
            .order_by(TranscriptUtterance.start_time_ms.asc())
        )
        return list(self.session.exec(statement).all())

    # Psychometric Report
    def save_report(self, report: PsychometricReport) -> PsychometricReport:
        self.session.add(report)
        self.session.commit()
        self.session.refresh(report)
        return report

    def get_report_by_session(self, session_id: str) -> Optional[PsychometricReport]:
        statement = select(PsychometricReport).where(PsychometricReport.session_id == session_id)
        return self.session.exec(statement).first()
