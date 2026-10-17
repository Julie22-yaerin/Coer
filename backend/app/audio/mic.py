import threading
import time
import logging
from typing import Callable, Optional
import numpy as np

logger = logging.getLogger(__name__)

class MicCapture:
    """
    Captures microphone audio (Founder voice) using PyAudio.
    """
    def __init__(self, on_audio_chunk: Callable[[bytes], None], sample_rate: int = 16000, chunk_size: int = 1600):
        self.on_audio_chunk = on_audio_chunk
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        logger.info("Microphone audio capture thread started.")

    def stop(self) -> None:
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        logger.info("Microphone audio capture thread stopped.")

    def _capture_loop(self) -> None:
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
            )

            try:
                while self._running:
                    data = stream.read(self.chunk_size, exception_on_overflow=False)
                    self.on_audio_chunk(data)
            finally:
                stream.stop_stream()
                stream.close()
                p.terminate()
        except Exception as e:
            logger.warning(f"PyAudio capture unavailable ({e}). Running in fallback mode.")
            while self._running:
                time.sleep(self.chunk_size / self.sample_rate)
                silence = np.zeros(self.chunk_size, dtype=np.int16).tobytes()
                self.on_audio_chunk(silence)
