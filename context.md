# PRODUCT SPECIFICATION & AGENT CONTEXT BLUEPRINT
# COER: UNDETECTABLE DESKTOP AI CO-FOUNDER COPILOT & MATCHING SYSTEM

> **AGENT DIRECTIVE & SSOT (SINGLE SOURCE OF TRUTH):**
> This file is the primary context and architectural blueprint for the AI Coding Agent working on the **Coer** repository (`Julie22-yaerin/Coer`). All subsequent development sessions, context extensions, code implementations, refactoring, and additions MUST strictly adhere to the technical specifications, coding rules, data models, and architectural patterns defined in this document.

---

## 1. SYSTEM OVERVIEW & PRODUCT SPECIFICATION

### 1.1 Executive Summary
**Coer** is an undetectable, stealth-mode desktop AI copilot designed for startup founders conducting discovery calls, interview screenings, and co-founder matchmaking conversations across video conferencing platforms (Zoom, Google Meet, Microsoft Teams, Slack Huddle, etc.).

Unlike conventional meeting bots (e.g., Otter.ai, Read.ai, Fireflies) that join calls as visible participant bots, **Coer runs 100% locally and stealthily on the founder's desktop**:
1. **Zero Bot Presence:** No virtual participant joins the call. No bot avatar, recording banner, or webhooks are triggered.
2. **OS-Level Stealth Audio Capture:** Audio is intercepted directly at the operating system hardware/driver level (speaker loopback + microphone stream) without injecting any code or browser extensions into video conferencing applications.
3. **Screen Share Invisibility:** The frontend UI widget utilizes OS-level display masking (`set_content_protected(true)` in Tauri) to remain completely invisible on screen shares and screen recording software.
4. **Sub-300ms Real-Time Guidance:** A frameless, transparent, floating widget provides instantaneous "What to ask next", situational advice, and red-flag alerts when the candidate pauses talking.
5. **Post-Meeting Psychometric & Compatibility Engine:** Automatically runs deep psychological synthesis (OCEAN Big Five personality profiling, core motivation vectors, and a Founder Complementarity Index) backed by timestamped transcript citations.

---

## 2. TECHNICAL ARCHITECTURE & STACK

```
+------------------------------------------------------------------------------------+
|                                COER DESKTOP APP                                    |
|                                                                                    |
|  +-------------------------------------+   WebSocket / IPC   +-------------------+  |
|  |     Tauri v2 Frontend (React 19)    | <=================> |  Python FastAPI   |  |
|  | - Transparent Frameless Overlay UI  |                     |  Backend Engine   |  |
|  | - Screen Share Invisibility Mask    |                     |  (Tauri Sidecar)  |  |
|  | - Global Shortcuts (Ctrl+Enter)     |                     +---------+---------+  |
|  | - Tailwind CSS + Lucide Icons       |                               |            |
|  +-------------------------------------+                               |            |
+------------------------------------------------------------------------|------------+
                                                                         |
                      +--------------------------------------------------+
                      |
                      v
+-------------------------------------------------------------------------------------+
|                              PYTHON BACKEND SUBSYSTEMS                              |
|                                                                                     |
|  [Audio Capture Engine]                                                             |
|  - Speaker Loopback (Candidate): `soundcard` library                                |
|  - Microphone Capture (User Founder): `pyaudio` library                             |
|  - Synchronized Audio Mixer: Resamples & mixes into 16kHz Mono Linear PCM Chunks    |
|                                                                                     |
|  [Real-Time STT Pipeline]                                                           |
|  - Deepgram Streaming API (WebSocket `wss://api.deepgram.com/v1/listen`)           |
|  - Fallback: Local `faster-whisper` thread worker                                   |
|  - VAD (Voice Activity Detection) & Silence Detection (>1.5s pause trigger)         |
|                                                                                     |
|  [LLM Suggestion & Analysis Layers]                                                 |
|  - Phase 1 (Real-Time Suggestions): Groq API / Together AI (`Llama-3.1-70b`)        |
|    * Latency target: <300ms Time-To-First-Token (TTFT)                              |
|  - Phase 2 (Post-Meeting Synthesis): OpenAI `gpt-4o` / Anthropic `Claude 3.5 Sonnet`|
|    * Deep psychometrics, OCEAN traits, Founder Complementarity Index (FCI)          |
|                                                                                     |
|  [Persistence Layer]                                                                |
|  - SQLite (WAL mode) via SQLModel / SQLAlchemy                                      |
|  - Stores: Transcripts, Utterances, Candidate Profiles, Psychometric Reports        |
+-------------------------------------------------------------------------------------+
```

### 2.1 Technology Stack Matrix
| Component | Primary Technology | Selection Rationale |
| :--- | :--- | :--- |
| **Desktop Shell** | **Tauri v2** (Rust Core) | Ultra-lightweight footprint (<40MB RAM), native OS window manipulation, screen share protection, fast binary startup. |
| **Frontend Framework** | **React 19 + TypeScript** | Strict type safety, modular component architecture, modern hook paradigms. |
| **Styling & Icons** | **Tailwind CSS + Lucide React** | Low-overhead utility classes, sleek dark-mode glassmorphism styling. |
| **Backend Engine** | **Python 3.11+ (FastAPI + AsyncIO)** | Native audio processing ecosystem, robust async WebSockets, AI/LLM SDK integration. Packaged as Tauri Sidecar. |
| **Speaker Audio (Candidate)** | **`soundcard` (Loopback)** | Captures internal system audio directly from the default output device without requiring virtual audio cables. |
| **Mic Audio (Founder)** | **`pyaudio` (CoreAudio / WASAPI)** | Low-latency local microphone audio capture with exact device channel mapping. |
| **Real-Time STT** | **Deepgram Streaming WebSocket** | <200ms latency, dual-channel diarization capability, automatic punctuation. Fallback: `faster-whisper`. |
| **Real-Time LLM (Phase 1)** | **Groq API (`Llama-3.1-70b-versatile`)** | Industry-leading inference speed (~300 tokens/sec, TTFT < 250ms) critical for real-time live assistance. |
| **Post-Meeting LLM (Phase 2)** | **OpenAI `gpt-4o` / Claude `3.5 Sonnet`** | Superior psychological reasoning, complex JSON schema formatting, nuanced trait synthesis. |
| **Database** | **SQLite (via SQLModel / SQLAlchemy)** | Zero-config, single-file local persistence, ACID compliant, easily queryable. |

---

## 3. CORE FEATURES & DETAILED PIPELINES (LUỒNG XỬ LÝ)

```
[System Loopback (Candidate)] ---> [Ring Buffer 1] --+
                                                     |---> [Synchronized Mixer] ---> 16kHz PCM (100ms)
[Microphone (Founder)]       ---> [Ring Buffer 2] --+                                       |
                                                                                            v
                                                                                [Deepgram WebSocket]
                                                                                            |
                                                                                     Live Utterance
                                                                                            |
                                                                                            v
                                            +-----------------------------------------------+
                                            |
                                            +---> [Rolling Sentence Buffer (Last 5-7)]
                                            |     - Candidate Silence > 1.5s Detect
                                            |     - Groq `Llama-3.1-70b` (<300ms)
                                            |     - Emit WS to Tauri Transparent Overlay
                                            |
                                            +---> [SQLite Local Storage]
                                                  - On Meeting "COMPLETED"
                                                  - OpenAI `GPT-4o` / Claude 3.5 Sonnet
                                                  - Extract OCEAN + FCI + Citations
                                                  - Save Final Psychometric Report
```

### 3.1 Feature 1: Dual-Stream Audio Capture & Synchronization
- **Goal:** Concurrently capture the candidate's voice (from system audio output) and the founder's voice (from microphone) with zero clock drift.
- **Detailed Mechanics:**
  1. **Thread 1 (Loopback Worker):** Uses `soundcard.get_loopback()` to continuously capture frames from default system speakers.
  2. **Thread 2 (Microphone Worker):** Uses `pyaudio.PyAudio().open(...)` with input stream to capture founder mic frames.
  3. **Thread-Safe Ring Buffers:** Both threads push raw audio bytes into memory-bounded `collections.deque(maxlen=100)` buffers.
  4. **Synchronized Mixing Engine:**
     - Downsamples / resamples both streams to mono 16,000 Hz, 16-bit linear PCM (`audio/x-raw`).
     - Normalizes gain levels to prevent clipping and balance volume.
     - Interleaves/mixes audio into 100ms chunks (3,200 bytes per chunk).
     - Tags channel metadata or diarization cues before streaming to the STT processor.

### 3.2 Feature 2: Sliding Window Real-Time Copilot (Frontend Widget)
- **Goal:** Deliver instant conversational intelligence without interrupting founder flow.
- **Detailed Mechanics:**
  1. **Sliding Context Window:** Maintains a real-time rolling deque of the last 5 to 7 transcribed utterances, annotated with speaker roles (`Candidate` vs `Founder`).
  2. **Silence / VAD Trigger:**
     - A voice activity detector (VAD) monitors candidate speech activity.
     - When candidate silence exceeds **1.5 seconds**, the system automatically dispatches the rolling context window to the Real-Time LLM pipeline.
  3. **Low-Latency LLM Request:**
     - Uses Groq API (`Llama-3.1-70b-versatile`) with a specialized, hyper-compressed system prompt.
     - Response constraints: Exactly 2 sharp follow-up questions + 1 tactical insight tip. Total response length < 60 tokens.
     - Total end-to-end latency: **<300ms**.
  4. **Tauri Stealth Widget Window:**
     - Frameless, transparent, `alwaysOnTop(true)`, decorum-free floating window.
     - Hidden from screen shares via OS display capture exclusion.
     - **Global Shortcut:** Intercepts `Ctrl + Enter` (or `Cmd + Enter` on macOS) to toggle window visibility or manually trigger an immediate suggestion re-prompt.

### 3.3 Feature 3: Post-Meeting Psychometric & Compatibility Engine
- **Goal:** Provide objective, evidence-based psychological evaluations of potential co-founders.
- **Detailed Mechanics:**
  1. **State Trigger:** When the founder clicks "End Meeting" or status is marked `COMPLETED`, the complete transcript is retrieved from SQLite.
  2. **Psychometric Extraction (OCEAN Big Five):**
     - **Openness:** Innovation, tolerance of ambiguity, willingness to pivot.
     - **Conscientiousness:** Execution rigor, discipline, operational thoroughness.
     - **Extraversion:** Energy source, pitching comfort, external vs internal focus.
     - **Agreeableness:** Conflict style, negotiation approach, team empathy vs bluntness.
     - **Neuroticism (Emotional Stability):** Stress response under startup chaos, resilience.
  3. **Core Motivations & Values:**
     - Autonomy, financial upside, impact, tech purism, equity expectations, risk appetite.
  4. **Founder Complementarity Index (FCI):**
     - Compares candidate's psychological profile with the founder's stored profile.
     - Calculates a compatibility score (0-100) across: Vision Alignment, Execution Complementarity, Conflict Resilience, and Cognitive Diversity.
  5. **Timestamped Evidence Requirement:**
     - Every metric score and insight MUST cite exact dialogue snippets with relative meeting timestamps (e.g., `[14:22] Candidate: "I usually prefer..."`).
     - Zero hallucinated scores; every insight is grounded in transcript evidence.

---

## 4. DATA SCHEMAS & DATABASE MODELS (SQLITE / SQLMODEL)

All models reside in `backend/app/models/` and utilize `sqlmodel` (or `pydantic` v2 + `sqlalchemy`).

### 4.1 SQLModel Database Schemas (`backend/app/models/schema.py`)
```python
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel

class FounderProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    role: str  # e.g., "Technical CEO", "Product Lead"
    vision_statement: str
    ocean_traits: Dict[str, float] = Field(default_factory=dict, sa_column_kwargs={"type_": "JSON"})
    key_values: List[str] = Field(default_factory=list, sa_column_kwargs={"type_": "JSON"})
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MeetingSession(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)  # UUID4
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
```

### 4.2 Real-Time WebSocket Message Contracts
```python
# Real-Time Suggestion Payload (Backend -> Frontend Widget)
class RealtimeSuggestionEvent(BaseModel):
    event_type: str = "suggestion"
    timestamp_ms: int
    trigger_reason: str  # "silence_timeout" | "manual_hotkey"
    last_context: List[str]
    suggested_questions: List[str]
    tactical_tip: Optional[str]
    latency_ms: float
```

---

## 5. CODING RULES, ARCHITECTURE CONSTRAINTS & QUALITY STANDARDS

### 5.1 Stealth & Security Constraints
1. **Zero Browser/Zoom Injection:** Never attempt to inject JavaScript, hook DOM elements, or inspect processes of Zoom, Google Meet, Teams, or Chrome. All capture occurs strictly at the OS audio device layer.
2. **Screen Capture Protection:** Every overlay window created in Tauri must set `set_content_protected(true)` (on macOS: `NSWindowSharingNone`, on Windows: `SetWindowDisplayAffinity(WDA_EXCLUDEFROMCAPTURE)`).
3. **No External Recording Bots:** No SIP or RTP bots are ever invited or connected to the conference bridge.

### 5.2 Memory Safety & Long-Running Session Stability
1. **Bounded Audio Queues:** Audio streams run for 1 to 2+ hours without interruption. Raw PCM buffers must use strict FIFO bounded deques with max length limits. Never allow unbounded list accumulation of uncompressed audio.
2. **Explicit Garbage Collection:** Audio chunks older than the sliding processing window must be actively dropped from memory once streamed to the STT provider.
3. **Connection Pooling:** SQLite sessions and HTTP/WebSocket client connections must use asynchronous context managers (`async with`) to prevent socket leaks.

### 5.3 Error Handling & Self-Healing Resilience
1. **Deepgram Reconnect Loop:** If the STT WebSocket disconnects, the audio capture thread must continue caching in a 5-second circular ring buffer while an async exponential-backoff reconnect loop re-establishes the socket. Under no circumstances may this crash the Tauri frontend.
2. **LLM Fallback Cascades:**
   - Real-time suggestions: Groq API -> Together AI -> Local heuristic fallback.
   - Post-meeting synthesis: OpenAI `gpt-4o` -> Anthropic `claude-3-5-sonnet` -> Local batch queue.
3. **UI Graceful Degradation:** The frontend overlay must display subtle connectivity pulses without intrusive popups or disruptive modals during a live meeting.

### 5.4 Decoupling & Async Architecture
1. **Strict UI & Engine Decoupling:** The Python backend audio parsing logic must run independently from the FastAPI route controllers. Audio threads communicate with async WebSocket handlers via `asyncio.Queue`.
2. **No Synchronous Audio Blocking:** Never call blocking I/O inside FastAPI async routes. Heavy calculations or local Whisper inference must run on dedicated background executor threads (`run_in_executor`).

### 5.5 Coding Style Requirements
- **Python:**
  - Type hints are mandatory on all function signatures (`def function(param: str) -> dict:`).
  - Use `Pydantic (v2)` and `SQLModel` for all data validation and persistence schemas.
  - Asynchronous first: use `async` / `await` for I/O, WebSockets, and network calls.
- **TypeScript & React:**
  - Functional components with strict TypeScript types only (`React.FC<Props>`).
  - No `any` types allowed. Use explicit types, interfaces, or generic parameters.
  - Logical, clean Tailwind CSS utility classes; avoid inline styles.

---

## 6. PROJECT DIRECTORY STRUCTURE & CODEBASE MAPPING

The repository leverages the existing Tauri v2 foundation (`pluely-master`) for stealth window management, OS permissions, and global shortcuts, while introducing the Python backend engine:

```
Coer/
├── context.md                    # THIS FILE - Master Architecture & Agent Context
├── README.md                     # Project documentation & setup guide
├── package.json                  # Root desktop app dependencies
├── src-tauri/                    # Tauri v2 Desktop Core (Rust)
│   ├── Cargo.toml                # Rust dependencies & permissions
│   ├── tauri.conf.json           # Window config (transparent, alwaysOnTop, sidecar)
│   ├── src/
│   │   ├── main.rs               # Tauri entrypoint
│   │   ├── lib.rs                # App setup & sidecar lifecycle
│   │   ├── window.rs             # Transparent & protected window management
│   │   └── shortcuts.rs          # Global shortcut handlers (Ctrl+Enter)
├── src/                          # Frontend Application (React 19 + TypeScript)
│   ├── index.html                # App shell
│   ├── App.tsx                   # Main router / view orchestrator
│   ├── components/
│   │   ├── overlay/              # Stealth Floating Copilot Widget
│   │   │   ├── CopilotWidget.tsx # Sliding window suggestion UI
│   │   │   └── SuggestionCard.tsx# Instant question chips & tactical tips
│   │   ├── dashboard/            # Founder Dashboard & Session History
│   │   │   ├── SessionList.tsx   # Past meetings list
│   │   │   └── ProfileEditor.tsx # Founder profile & trait baseline
│   │   └── reports/              # Post-Meeting Psychometric Views
│   │       ├── OceanChart.tsx    # OCEAN Big Five spider/bar chart
│   │       ├── MatchIndex.tsx    # Founder Complementarity Index visualizer
│   │       └── EvidenceList.tsx  # Transcript quote citations
│   ├── hooks/
│   │   ├── useAudioStream.ts     # Audio capture status hook
│   │   ├── useCopilotSocket.ts   # WebSocket connection to Python backend
│   │   └── useGlobalShortcuts.ts # Hotkey listener hook
│   └── types/
│       └── coer.d.ts             # Shared TypeScript type definitions
└── backend/                      # Python FastAPI Engine (Tauri Sidecar)
    ├── pyproject.toml            # Poetry / uv / pip dependencies
    ├── requirements.txt          # Python dependencies
    ├── run.py                    # Entrypoint script for sidecar execution
    └── app/
        ├── main.py               # FastAPI application & WebSocket server
        ├── config.py             # Environment settings & API keys
        ├── audio/                # Dual-stream capture & mixing engine
        │   ├── loopback.py       # Soundcard speaker capture
        │   ├── mic.py            # PyAudio microphone capture
        │   └── mixer.py          # PCM resampler & 16kHz buffer mixer
        ├── stt/                  # Speech-to-Text streaming
        │   ├── deepgram_client.py# Deepgram live streaming WebSocket client
        │   └── whisper_local.py  # Local faster-whisper fallback worker
        ├── llm/                  # Intelligence & Copilot Prompts
        │   ├── copilot_stream.py # Groq Llama-3.1-70b sub-300ms suggestion generator
        │   └── prompts.py        # System prompts & prompt compression rules
        ├── analysis/             # Post-Meeting Psychometric Engine
        │   ├── ocean_scorer.py   # Big Five trait extractor
        │   ├── compatibility.py  # Founder Complementarity Index (FCI) algorithm
        │   └── synthesizer.py    # OpenAI/Claude post-call report generator
        ├── db/                   # Database & Storage
        │   ├── session.py        # SQLite database connection & WAL settings
        │   └── repository.py     # Data access methods
        └── models/               # Pydantic v2 & SQLModel schemas
            └── schema.py         # Full data contracts
```

---

## 7. STEP-BY-STEP IMPLEMENTATION ROADMAP FOR CODING AGENT

When working on upcoming tasks, execute according to this structured roadmap:

### Phase 1: Environment & Sidecar Architecture Setup
- [ ] Configure Python backend dependencies in `backend/pyproject.toml` and `backend/requirements.txt` (`fastapi`, `uvicorn`, `soundcard`, `pyaudio`, `deepgram-sdk`, `groq`, `sqlmodel`, `openai`, `anthropic`).
- [ ] Implement `backend/run.py` and `backend/app/main.py` with FastAPI WebSocket endpoint `/ws/copilot` and REST health check endpoints.
- [ ] Verify Tauri v2 sidecar configuration in `src-tauri/tauri.conf.json` to launch the Python backend daemon.

### Phase 2: Dual-Stream Audio Capture Engine
- [ ] Implement `backend/app/audio/loopback.py`: System audio capture via `soundcard`.
- [ ] Implement `backend/app/audio/mic.py`: Microphone audio capture via `pyaudio`.
- [ ] Implement `backend/app/audio/mixer.py`: Synchronized ring buffer, 16kHz mono 16-bit linear PCM conversion, gain normalization, and 100ms chunk generation.
- [ ] Unit test audio stream mixing locally with simulated buffer inputs.

### Phase 3: Real-Time STT & Sliding Window VAD
- [ ] Implement `backend/app/stt/deepgram_client.py`: WebSocket streaming client connected to Deepgram with automatic reconnect on failure.
- [ ] Implement rolling transcript buffer (last 5-7 utterances) with speaker tags (`founder` vs `candidate`).
- [ ] Implement 1.5s candidate silence detection logic to trigger the suggestion pipeline.

### Phase 4: Sub-300ms Suggestion Pipeline (Groq Llama-3.1-70b)
- [ ] Implement `backend/app/llm/copilot_stream.py`: Optimized Groq client invoking `Llama-3.1-70b-versatile`.
- [ ] Craft latency-optimized system prompt returning structured question recommendations and tactical insights.
- [ ] Stream suggestions over WebSocket to the Tauri frontend in real-time.

### Phase 5: Stealth Desktop Widget & Global Shortcut
- [ ] Build the transparent, frameless, floating React widget (`src/components/overlay/CopilotWidget.tsx`).
- [ ] Integrate Tauri window APIs for `alwaysOnTop` and screen share capture masking.
- [ ] Bind global shortcut `Ctrl + Enter` (or `Cmd + Enter`) to toggle widget visibility or force an immediate re-prompt.

### Phase 6: Post-Meeting Psychometric & Compatibility Engine
- [ ] Implement SQLite schema and migrations in `backend/app/models/schema.py` and `backend/app/db/session.py`.
- [ ] Implement `backend/app/analysis/ocean_scorer.py`: OCEAN trait extraction with timestamped evidence quotes.
- [ ] Implement `backend/app/analysis/compatibility.py`: Founder Complementarity Index (FCI) algorithm.
- [ ] Implement `backend/app/analysis/synthesizer.py`: Deep report generation using `GPT-4o` or `Claude 3.5 Sonnet`.
- [ ] Build the Post-Meeting Report UI in React (`src/components/reports/`).

### Phase 7: Hardening, Memory Safety & Verification
- [ ] Profile memory usage under a simulated 2-hour continuous audio stream to ensure zero memory leaks.
- [ ] Test STT disconnection and automatic recovery mechanisms without UI freezing.
- [ ] Verify end-to-end latency benchmarks (<300ms suggestion delivery).

---

## 8. ENVIRONMENT VARIABLES & SECRETS CONFIGURATION

Create `.env` in `backend/` and project root for local development:
```bash
# Deepgram Streaming STT
DEEPGRAM_API_KEY="your-deepgram-api-key"

# Real-Time Suggestion LLM (<300ms)
GROQ_API_KEY="your-groq-api-key"
TOGETHER_API_KEY="your-together-api-key"  # Optional fallback

# Post-Meeting Deep Synthesis LLM
OPENAI_API_KEY="your-openai-api-key"
ANTHROPIC_API_KEY="your-anthropic-api-key"

# Database Configuration
DATABASE_URL="sqlite:///./coer.db"

# Server Settings
BACKEND_HOST="127.0.0.1"
BACKEND_PORT=8765
DEBUG=True
```

---

> **FINAL INSTRUCTION TO AGENT:** When executing any future user request or context, open this file, read the relevant section, follow all constraints, and update the implementation checklist as milestones are reached.
