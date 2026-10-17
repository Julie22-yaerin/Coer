import { useState, useEffect, useRef, useCallback } from "react";
import {
  RealtimeSuggestionEvent,
  RealtimeTranscriptEvent,
  SessionStatusEvent,
  PsychometricReport,
} from "../types/coer";

interface UseCopilotSocketOptions {
  url?: string;
  autoConnect?: boolean;
}

export function useCopilotSocket(options: UseCopilotSocketOptions = {}) {
  const { url = "ws://127.0.0.1:8765/ws/copilot", autoConnect = true } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [latestSuggestion, setLatestSuggestion] = useState<RealtimeSuggestionEvent | null>(null);
  const [transcripts, setTranscripts] = useState<RealtimeTranscriptEvent[]>([]);
  const [completedReport, setCompletedReport] = useState<PsychometricReport | null>(null);
  const [error, setError] = useState<string | null>(null);

  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    if (socketRef.current?.readyState === WebSocket.OPEN) return;

    try {
      const ws = new WebSocket(url);

      ws.onopen = () => {
        setIsConnected(true);
        setError(null);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.event_type === "suggestion") {
            setLatestSuggestion(data as RealtimeSuggestionEvent);
          } else if (data.event_type === "transcript") {
            setTranscripts((prev) => [...prev, data as RealtimeTranscriptEvent]);
          } else if (data.event_type === "report") {
            setCompletedReport(data.report as PsychometricReport);
          }
        } catch (e) {
          console.error("Failed to parse websocket message:", e);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        // Exponential reconnect
        reconnectTimeoutRef.current = setTimeout(connect, 2000);
      };

      ws.onerror = (err) => {
        console.error("Copilot WebSocket error:", err);
        setError("WebSocket connection failed");
      };

      socketRef.current = ws;
    } catch (err) {
      setError(String(err));
    }
  }, [url]);

  useEffect(() => {
    if (autoConnect) {
      connect();
    }
    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      socketRef.current?.close();
    };
  }, [autoConnect, connect]);

  const sendAction = useCallback((payload: Record<string, unknown>) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(payload));
    }
  }, []);

  const requestSuggestion = useCallback(() => {
    sendAction({ action: "request_suggestion" });
  }, [sendAction]);

  const startSession = useCallback(
    (sessionId: string) => {
      setTranscripts([]);
      setLatestSuggestion(null);
      setCompletedReport(null);
      sendAction({ action: "start_session", session_id: sessionId });
    },
    [sendAction]
  );

  const endSession = useCallback(
    (sessionId: string) => {
      sendAction({ action: "end_session", session_id: sessionId });
    },
    [sendAction]
  );

  return {
    isConnected,
    error,
    latestSuggestion,
    transcripts,
    completedReport,
    requestSuggestion,
    startSession,
    endSession,
    connect,
  };
}
