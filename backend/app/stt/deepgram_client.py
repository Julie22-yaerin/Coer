import asyncio
import json
import logging
import time
from typing import Callable, Optional
import websockets

logger = logging.getLogger(__name__)

class DeepgramStreamingClient:
    """
    Real-Time STT Client streaming to Deepgram WebSocket:
    - Auto-reconnect loop with exponential backoff
    - Utterance parsing and speaker diarization routing
    - Emits structured transcript events
    """
    def __init__(
        self,
        api_key: str,
        on_utterance: Callable[[str, str, int, int, float], None],
        sample_rate: int = 16000,
    ):
        self.api_key = api_key
        self.on_utterance = on_utterance
        self.sample_rate = sample_rate
        self._running = False
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._audio_queue: asyncio.Queue[bytes] = asyncio.Queue(maxsize=100)
        self._worker_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._worker_task = asyncio.create_task(self._connection_manager())
        logger.info("Deepgram streaming manager initiated.")

    async def stop(self) -> None:
        self._running = False
        if self._ws:
            try:
                await self._ws.close()
            except Exception:
                pass
        if self._worker_task:
            self._worker_task.cancel()
        logger.info("Deepgram streaming client stopped.")

    async def send_audio(self, chunk: bytes) -> None:
        if self._running:
            try:
                self._audio_queue.put_nowait(chunk)
            except asyncio.QueueFull:
                # Discard oldest chunk in buffer to prevent lag
                try:
                    self._audio_queue.get_nowait()
                    self._audio_queue.put_nowait(chunk)
                except Exception:
                    pass

    async def _connection_manager(self) -> None:
        if not self.api_key:
            logger.warning("Deepgram API key not configured. Streaming STT running in mock mode.")
            return

        url = (
            f"wss://api.deepgram.com/v1/listen?"
            f"encoding=linear16&sample_rate={self.sample_rate}&channels=1"
            f"&punctuate=true&interim_results=false&smart_format=true&diarize=true"
        )
        headers = {"Authorization": f"Token {self.api_key}"}

        backoff = 1.0
        while self._running:
            try:
                async with websockets.connect(url, extra_headers=headers) as ws:
                    self._ws = ws
                    backoff = 1.0
                    logger.info("Connected to Deepgram WebSocket.")

                    send_task = asyncio.create_task(self._send_loop(ws))
                    recv_task = asyncio.create_task(self._recv_loop(ws))

                    done, pending = await asyncio.wait(
                        [send_task, recv_task],
                        return_when=asyncio.FIRST_COMPLETED,
                    )

                    for task in pending:
                        task.cancel()
            except Exception as e:
                logger.error(f"Deepgram WebSocket error: {e}. Reconnecting in {backoff:.1f}s...")
                await asyncio.sleep(backoff)
                backoff = min(backoff * 1.5, 10.0)

    async def _send_loop(self, ws: websockets.WebSocketClientProtocol) -> None:
        while self._running:
            chunk = await self._audio_queue.get()
            try:
                await ws.send(chunk)
            except Exception as e:
                logger.error(f"Failed to send audio chunk: {e}")
                break

    async def _recv_loop(self, ws: websockets.WebSocketClientProtocol) -> None:
        async for message in ws:
            try:
                data = json.loads(message)
                channel = data.get("channel", {})
                alternatives = channel.get("alternatives", [])
                if alternatives:
                    transcript = alternatives[0].get("transcript", "").strip()
                    if transcript:
                        confidence = alternatives[0].get("confidence", 1.0)
                        start_time = int(data.get("start", 0) * 1000)
                        duration = int(data.get("duration", 0) * 1000)
                        
                        # Guess speaker from diarization or default
                        words = alternatives[0].get("words", [])
                        speaker = "candidate"
                        if words and "speaker" in words[0]:
                            speaker = "founder" if words[0]["speaker"] == 0 else "candidate"

                        self.on_utterance(
                            speaker,
                            transcript,
                            start_time,
                            start_time + duration,
                            confidence,
                        )
            except Exception as e:
                logger.error(f"Error parsing Deepgram message: {e}")
