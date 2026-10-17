# Coer: Undetectable Desktop AI Co-founder Copilot & Matching System

> **Stealth-mode, real-time AI copilot and post-meeting psychometric evaluation engine for startup founder interviews and co-founder matchmaking.**

---

## 🚀 Overview

**Coer** is an undetectable, stealth-mode desktop AI copilot designed for startup founders conducting discovery calls, interview screenings, and co-founder matchmaking conversations across video conferencing platforms (Zoom, Google Meet, Microsoft Teams, Slack Huddle, etc.).

Unlike conventional meeting bots (e.g., Otter.ai, Read.ai, Fireflies) that join calls as visible participant bots:
1. **Zero Bot Presence:** No virtual bot joins the call. No bot avatar, recording banner, or webhooks are triggered.
2. **OS-Level Stealth Audio Capture:** Audio is intercepted directly at the operating system hardware/driver level (speaker loopback + microphone stream) without injecting code into browsers or conference apps.
3. **Screen Share Invisibility:** The frontend UI widget utilizes OS-level display masking (`set_content_protected(true)` in Tauri) to remain completely invisible on screen shares and screen recordings.
4. **Sub-300ms Real-Time Guidance:** A frameless, transparent, floating widget provides instantaneous "What to ask next", situational advice, and red-flag alerts when the candidate pauses talking (>1.5s silence).
5. **Post-Meeting Psychometric & Compatibility Engine:** Automatically runs deep psychological synthesis (OCEAN Big Five personality profiling, core motivation vectors, and a Founder Complementarity Index) backed by timestamped transcript citations.

---

## 🛠️ Architecture & Tech Stack

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
|  - Phase 1 (Real-Time Suggestions): Groq API (`Llama-3.1-70b-versatile`, <300ms)    |
|  - Phase 2 (Post-Meeting Synthesis): OpenAI `gpt-4o` / Anthropic `Claude 3.5 Sonnet`|
|                                                                                     |
|  [Persistence Layer]                                                                |
|  - SQLite (WAL mode) via SQLModel / SQLAlchemy                                      |
+-------------------------------------------------------------------------------------+
```

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Desktop Shell** | **Tauri v2 (Rust Core)** | <40MB RAM footprint, native window protection, screen share invisibility |
| **Frontend UI** | **React 19 + TypeScript + Tailwind CSS** | Strict type safety, glassmorphism overlay, responsive dashboard |
| **Backend Engine** | **Python 3.11+ (FastAPI + AsyncIO)** | Native audio processing ecosystem, packaged as Tauri Sidecar |
| **Audio Loopback** | **`soundcard` (Candidate speaker loopback)** | OS-level capture without virtual audio cables |
| **Microphone** | **`pyaudio` (Founder local mic)** | Low-latency input capture with hardware channel mapping |
| **Real-Time STT** | **Deepgram Streaming WebSocket** | <200ms dual-channel transcription; fallback to `faster-whisper` |
| **Real-Time LLM** | **Groq API (`Llama-3.1-70b`)** | TTFT < 250ms, ultra-low latency prompt responses |
| **Psychometrics** | **OpenAI `GPT-4o` / Anthropic `Claude 3.5`** | OCEAN Big 5 scoring & Founder Complementarity Index (FCI) |
| **Persistence** | **SQLite (SQLModel / SQLAlchemy)** | Zero-config, single-file local persistence with WAL mode |

---

## 📂 Project Structure

```
Coer/
├── context.md                    # Single Source of Truth (SSOT) Architecture Blueprint
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
│   ├── components/               # UI components (overlay, dashboard, reports)
│   ├── hooks/                    # React hooks for audio, sockets, and shortcuts
│   └── types/                    # TypeScript interfaces & types
└── backend/                      # Python FastAPI Engine (Tauri Sidecar)
    ├── pyproject.toml            # Dependencies definition
    ├── requirements.txt          # Python dependencies
    ├── run.py                    # Entrypoint script for sidecar execution
    └── app/
        ├── main.py               # FastAPI application & WebSocket server
        ├── config.py             # Environment configuration
        ├── audio/                # Dual-stream loopback + mic mixer
        ├── stt/                  # Deepgram streaming client & whisper fallback
        ├── llm/                  # Groq sub-300ms suggestion generator
        ├── analysis/             # OCEAN psychometric & FCI scoring
        ├── db/                   # SQLite database & repository
        └── models/               # SQLModel / Pydantic schemas
```

---

## ⚡ Quick Start

### 1. Prerequisites
- **Node.js** >= 18
- **Rust** >= 1.77 (`curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`)
- **Python** >= 3.11

### 2. Frontend & Tauri Desktop Setup
```bash
# Install dependencies
npm install

# Run frontend in development mode
npm run dev

# Run Tauri desktop app
npm run tauri dev
```

### 3. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run backend server
python run.py
```

### 4. Environment Variables
Create `.env` in `backend/` or the project root:
```bash
# STT & LLM API Keys
DEEPGRAM_API_KEY="your-deepgram-api-key"
GROQ_API_KEY="your-groq-api-key"
OPENAI_API_KEY="your-openai-api-key"
ANTHROPIC_API_KEY="your-anthropic-api-key"

# Database & Server
DATABASE_URL="sqlite:///./coer.db"
BACKEND_HOST="127.0.0.1"
BACKEND_PORT=8765
DEBUG=True
```

---

## 📄 License
Licensed under the [GPL-3.0 License](LICENSE).