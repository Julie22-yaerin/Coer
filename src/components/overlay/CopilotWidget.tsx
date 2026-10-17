import React, { useEffect } from "react";
import { useCopilotSocket } from "../../hooks/useCopilotSocket";
import { SuggestionCard } from "./SuggestionCard";
import { Mic, ShieldCheck, Zap } from "lucide-react";

export const CopilotWidget: React.FC = () => {
  const { isConnected, latestSuggestion, requestSuggestion } = useCopilotSocket();

  // Listen for Ctrl+Enter or Cmd+Enter to manually trigger suggestion
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        e.preventDefault();
        requestSuggestion();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [requestSuggestion]);

  return (
    <div className="w-full max-w-xl mx-auto select-none font-sans">
      <div className="relative overflow-hidden rounded-2xl bg-neutral-950/80 backdrop-blur-xl border border-white/10 shadow-2xl p-2.5 flex flex-col gap-2">
        {/* Top Status Bar */}
        <div className="flex items-center justify-between px-2 text-[11px] text-neutral-400">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-white tracking-wide">COER</span>
            <span className="text-[10px] text-neutral-500 font-mono">v0.1.0</span>
            <div className="flex items-center gap-1 text-[10px] text-emerald-400/90 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">
              <ShieldCheck className="w-3 h-3" />
              <span>Stealth Active</span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[10px] text-neutral-400 font-mono flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 text-[9px] bg-neutral-800 rounded border border-neutral-700 text-neutral-300">
                ⌘/Ctrl + ↵
              </kbd>
            </span>
            <div
              className={`w-2 h-2 rounded-full ${
                isConnected ? "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" : "bg-neutral-600"
              }`}
              title={isConnected ? "Engine Connected" : "Connecting..."}
            />
          </div>
        </div>

        {/* Suggestion Card */}
        <SuggestionCard suggestion={latestSuggestion} />
      </div>
    </div>
  );
};
