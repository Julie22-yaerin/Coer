import asyncio
import json
import logging
import time
from typing import List, Optional, Tuple

from app.config import settings
from app.llm.prompts import REALTIME_COPILOT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class CopilotStreamEngine:
    """
    Real-Time LLM Suggestion Engine:
    - Primary: Groq API (Llama-3.1-70b-versatile)
    - Fallback: Heuristic rule-based suggestions
    - Measures Time-To-First-Token (TTFT) and total latency
    """
    def __init__(self, groq_api_key: Optional[str] = None):
        self.api_key = groq_api_key or settings.GROQ_API_KEY
        self._groq_client = None
        if self.api_key:
            try:
                from groq import AsyncGroq
                self._groq_client = AsyncGroq(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}")

    async def generate_suggestions(
        self, context_utterances: List[str], trigger_reason: str = "silence_timeout"
    ) -> Tuple[List[str], Optional[str], float]:
        start_time = time.time()
        
        if self._groq_client and context_utterances:
            try:
                dialogue = "\n".join(context_utterances[-7:])
                messages = [
                    {"role": "system", "content": REALTIME_COPILOT_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Recent Conversation:\n{dialogue}\n\nCandidate just paused. Suggest next steps:"}
                ]

                response = await self._groq_client.chat.completions.create(
                    model="llama-3.1-70b-versatile",
                    messages=messages,
                    temperature=0.3,
                    max_tokens=80,
                    response_format={"type": "json_object"},
                )

                latency_ms = (time.time() - start_time) * 1000.0
                content = response.choices[0].message.content
                data = json.loads(content)
                questions = data.get("questions", [])[:2]
                tip = data.get("tip")
                return questions, tip, latency_ms
            except Exception as e:
                logger.error(f"Groq generation failed: {e}. Falling back to heuristics.")

        # Heuristic fallback (<5ms latency)
        latency_ms = (time.time() - start_time) * 1000.0
        questions = [
            "What was the single hardest tradeoff you had to make on that project?",
            "How did your team handle the friction when timelines slipped?",
        ]
        tip = "Dig deeper into accountability vs blame."
        return questions, tip, latency_ms
