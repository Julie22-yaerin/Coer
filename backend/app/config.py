import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # STT & LLM Providers
    DEEPGRAM_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    TOGETHER_API_KEY: Optional[str] = None
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # Database
    DATABASE_URL: str = "sqlite:///./coer.db"

    # Server Settings
    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8765
    DEBUG: bool = True

    # Real-time Tuning
    SILENCE_THRESHOLD_SEC: float = 1.5
    MAX_CONTEXT_UTTERANCES: int = 7
    AUDIO_SAMPLE_RATE: int = 16000
    AUDIO_CHUNK_MS: int = 100

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
