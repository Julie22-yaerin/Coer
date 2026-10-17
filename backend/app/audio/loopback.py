import threading
import time
import logging
from typing import Callable, Optional
import numpy as np

logger = logging.getLogger(__name__)

class LoopbackCapture:
    """
    Captures speaker loopback audio (Candidate speech from Zoom/Meet/Teams)
    using the `soundcard` library.
    """
    def __init__(self, on_audio_chunk: Callable[[bytes], None], sample_rate: int = 48000, chunk_size: int = 4800):
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
        logger.info("Loopback audio capture thread started.")

    def stop(self) -> None:
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        logger.info("Loopback audio capture thread stopped.")

    def _capture_loop(self) -> None:
        try:
            import soundcard as sc
            speaker = sc.default_speaker()
            loopback_mic = sc.get_microphone(id=speaker.id, include_loopback=True)
            
            with loopback_mic.recorder(samplerate=self.sample_rate, channels=1) as mic:
                while self._running:
                    data = mic.record(numframes=self.chunk_size)
                    # Convert float32 [-1.0, 1.0] to int16 bytes
                    int16_data = (np.clip(data, -1.0, 1.0) * 32767).astype(np.int16)
                    self.on_audio_chunk(int16_data.tobytes())
        except Exception as e:
            logger.warning(f"Native soundcard loopback capture unavailable ({e}). Running in fallback mode.")
            # Fallback simulation or silence generator for environments without loopback driver
            while self._running:
                time.sleep(self.chunk_size / self.sample_rate)
                # Send silence chunk in int16
                silence = np.zeros(self.chunk_size, dtype=np.int16).tobytes()
                self.on_audio_chunk(silence)
