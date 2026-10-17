import logging
from typing import Optional, Callable
import numpy as np

logger = logging.getLogger(__name__)

class WhisperLocalFallback:
    """
    Fallback local transcription worker using faster-whisper or offline fallback.
    """
    def __init__(self, on_utterance: Optional[Callable[[str, str, int, int, float], None]] = None):
        self.on_utterance = on_utterance
        self.model = None

    def initialize(self) -> bool:
        try:
            from faster_whisper import WhisperModel
            self.model = WhisperModel("base.en", device="cpu", compute_type="int8")
            logger.info("Local faster-whisper initialized.")
            return True
        except Exception as e:
            logger.warning(f"faster-whisper not available: {e}. Running in local mock mode.")
            return False

    def transcribe_chunk(self, audio_bytes: bytes, speaker: str = "candidate") -> Optional[str]:
        if not self.model:
            return None
        try:
            audio_data = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            segments, _ = self.model.transcribe(audio_data, beam_size=1)
            texts = [segment.text for segment in segments]
            return " ".join(texts).strip()
        except Exception as e:
            logger.error(f"Local whisper error: {e}")
            return None
