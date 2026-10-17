/**
 * Coer TypeScript Type Definitions
 * Shared types for Real-Time Copilot, Psychometrics, and Meeting Sessions.
 */

export interface FounderProfile {
  id?: number;
  name: string;
  role: string;
  vision_statement: string;
  ocean_traits: {
    ocean_openness?: number;
    ocean_conscientiousness?: number;
    ocean_extraversion?: number;
    ocean_agreeableness?: number;
    ocean_neuroticism?: number;
    [key: string]: number | undefined;
  };
  key_values: string[];
  created_at?: string;
}

export interface MeetingSession {
  id: string;
  candidate_name: string;
  target_role: string;
  status: "IN_PROGRESS" | "COMPLETED" | "FAILED";
  started_at: string;
  ended_at?: string | null;
  total_duration_sec?: number | null;
  audio_path?: string | null;
}

export interface TranscriptUtterance {
  id?: number;
  session_id: string;
  speaker: "founder" | "candidate";
  text: string;
  start_time_ms: number;
  end_time_ms: number;
  confidence: number;
  created_at?: string;
}

export interface EvidenceCitation {
  trait: string;
  timestamp: string;
  quote: string;
  reasoning: string;
}

export interface PsychometricReport {
  id?: number;
  session_id: string;
  ocean_openness: number;
  ocean_conscientiousness: number;
  ocean_extraversion: number;
  ocean_agreeableness: number;
  ocean_neuroticism: number;
  complementarity_index: number;
  motivation_drivers: string[];
  red_flags: string[];
  strengths: string[];
  evidence_citations: EvidenceCitation[];
  full_markdown_report: string;
  created_at?: string;
}

export interface RealtimeSuggestionEvent {
  event_type: "suggestion";
  timestamp_ms: number;
  trigger_reason: "silence_timeout" | "manual_hotkey";
  last_context: string[];
  suggested_questions: string[];
  tactical_tip?: string | null;
  latency_ms: number;
}

export interface RealtimeTranscriptEvent {
  event_type: "transcript";
  session_id: string;
  speaker: "founder" | "candidate";
  text: string;
  start_time_ms: number;
  end_time_ms: number;
}

export interface SessionStatusEvent {
  event_type: "status";
  status: string;
  session_id: string;
  message?: string;
}
