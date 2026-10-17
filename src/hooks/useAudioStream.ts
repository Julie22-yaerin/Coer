import { useState, useCallback, useRef } from "react";
import { invoke } from "@tauri-apps/api/core";

export interface AudioStreamState {
  isCapturing: boolean;
  loopbackActive: boolean;
  micActive: boolean;
  error: string | null;
}

export function useAudioStream() {
  const [state, setState] = useState<AudioStreamState>({
    isCapturing: false,
    loopbackActive: false,
    micActive: false,
    error: null,
  });

  const startStream = useCallback(async () => {
    try {
      setState((prev) => ({
        ...prev,
        isCapturing: true,
        loopbackActive: true,
        micActive: true,
        error: null,
      }));
    } catch (err) {
      setState((prev) => ({
        ...prev,
        isCapturing: false,
        error: String(err),
      }));
    }
  }, []);

  const stopStream = useCallback(async () => {
    setState((prev) => ({
      ...prev,
      isCapturing: false,
      loopbackActive: false,
      micActive: false,
    }));
  }, []);

  return {
    ...state,
    startStream,
    stopStream,
  };
}
