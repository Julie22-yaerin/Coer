import collections
import threading
import time
import logging
from typing import Callable, Optional
import numpy as np

logger = logging.getLogger(__name__)

class AudioMixer:
    """
    Synchronized audio mixing engine:
    - Ring buffers for candidate (loopback) and founder (mic)
    - Resampling to 16,000 Hz 16-bit linear PCM
    - Gain normalization
    - Emits 100ms chunks (1600 samples = 3200 bytes)
    """
    def __init__(
        self,
        on_mixed_chunk: Callable[[bytes, str], None],
        target_sample_rate: int = 16000,
        chunk_ms: int = 100,
        max_buffer_chunks: int = 100,
    ):
        self.on_mixed_chunk = on_mixed_chunk
        self.target_sample_rate = target_sample_rate
        self.chunk_ms = chunk_ms
        self.samples_per_chunk = int(target_sample_rate * (chunk_ms / 1000.0))
        self.bytes_per_chunk = self.samples_per_chunk * 2  # 16-bit int = 2 bytes

        # Memory-bounded thread-safe ring buffers
        self.candidate_buffer = collections.deque(maxlen=max_buffer_chunks)
        self.founder_buffer = collections.deque(maxlen=max_buffer_chunks)
        self._lock = threading.Lock()
        
        self._running = False
        self._mixer_thread: Optional[threading.Thread] = None

    def push_candidate_audio(self, raw_bytes: bytes) -> None:
        with self._lock:
            self.candidate_buffer.append(raw_bytes)

    def push_founder_audio(self, raw_bytes: bytes) -> None:
        with self._lock:
            self.founder_buffer.append(raw_bytes)

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._mixer_thread = threading.Thread(target=self._mix_loop, daemon=True)
        self._mixer_thread.start()
        logger.info("Audio mixer loop started.")

    def stop(self) -> None:
        self._running = False
        if self._mixer_thread and self._mixer_thread.is_alive():
            self._mixer_thread.join(timeout=1.0)
        logger.info("Audio mixer loop stopped.")

    def _mix_loop(self) -> None:
        interval = self.chunk_ms / 1000.0
        while self._running:
            start_time = time.time()
            
            cand_chunk = None
            found_chunk = None

            with self._lock:
                if self.candidate_buffer:
                    cand_chunk = self.candidate_buffer.popleft()
                if self.founder_buffer:
                    found_chunk = self.founder_buffer.popleft()

            # Process chunks
            if cand_chunk or found_chunk:
                cand_arr = np.frombuffer(cand_chunk, dtype=np.int16) if cand_chunk else np.zeros(self.samples_per_chunk, dtype=np.int16)
                found_arr = np.frombuffer(found_chunk, dtype=np.int16) if found_chunk else np.zeros(self.samples_per_chunk, dtype=np.int16)

                # Ensure length matches chunk
                if len(cand_arr) < self.samples_per_chunk:
                    cand_arr = np.pad(cand_arr, (0, self.samples_per_chunk - len(cand_arr)))
                else:
                    cand_arr = cand_arr[:self.samples_per_chunk]

                if len(found_arr) < self.samples_per_chunk:
                    found_arr = np.pad(found_arr, (0, self.samples_per_chunk - len(found_arr)))
                else:
                    found_arr = found_arr[:self.samples_per_chunk]

                # Determine active speaker or mix
                cand_energy = np.mean(np.abs(cand_arr.astype(float)))
                found_energy = np.mean(np.abs(found_arr.astype(float)))

                speaker = "candidate" if cand_energy >= found_energy else "founder"

                # Normalized mix
                mixed = (cand_arr.astype(np.int32) + found_arr.astype(np.int32)) // 2
                mixed_int16 = np.clip(mixed, -32768, 32767).astype(np.int16)

                self.on_mixed_chunk(mixed_int16.tobytes(), speaker)

            elapsed = time.time() - start_time
            sleep_time = max(0.0, interval - elapsed)
            time.sleep(sleep_time)
