import React from "react";
import { Sparkles, HelpCircle, Lightbulb } from "lucide-react";
import { RealtimeSuggestionEvent } from "../../types/coer";

interface SuggestionCardProps {
  suggestion: RealtimeSuggestionEvent | null;
  onSelectQuestion?: (question: string) => void;
}

export const SuggestionCard: React.FC<SuggestionCardProps> = ({
  suggestion,
  onSelectQuestion,
}) => {
  if (!suggestion) {
    return (
      <div className="flex items-center gap-2 text-xs text-neutral-400 py-1 px-3">
        <Sparkles className="w-3.5 h-3.5 text-neutral-500 animate-pulse" />
        <span>Listening in stealth mode... Sub-300ms advice will appear here</span>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-2 p-3 bg-neutral-900/90 backdrop-blur-md rounded-xl border border-white/10 text-white shadow-2xl">
      {/* Header & Latency Badge */}
      <div className="flex items-center justify-between text-[11px] text-neutral-400">
        <div className="flex items-center gap-1.5 font-medium text-emerald-400">
          <Sparkles className="w-3 h-3" />
          <span>Real-time Guidance</span>
          <span className="text-[10px] text-neutral-500 font-mono">
            ({Math.round(suggestion.latency_ms)}ms)
          </span>
        </div>
        <span className="text-[10px] uppercase tracking-wider text-neutral-500">
          {suggestion.trigger_reason === "silence_timeout" ? "1.5s Pause" : "Hot-key"}
        </span>
      </div>

      {/* Suggested Questions */}
      <div className="flex flex-col gap-1.5">
        {suggestion.suggested_questions.map((q, idx) => (
          <button
            key={idx}
            onClick={() => onSelectQuestion?.(q)}
            className="flex items-start gap-2 text-left text-xs bg-white/5 hover:bg-white/10 transition-colors p-2 rounded-lg border border-white/5 group"
          >
            <HelpCircle className="w-3.5 h-3.5 text-emerald-400 mt-0.5 shrink-0 group-hover:scale-110 transition-transform" />
            <span className="text-neutral-200 font-normal leading-relaxed">{q}</span>
          </button>
        ))}
      </div>

      {/* Tactical Tip */}
      {suggestion.tactical_tip && (
        <div className="flex items-center gap-2 text-[11px] text-amber-300/90 bg-amber-500/10 px-2.5 py-1.5 rounded-lg border border-amber-500/20">
          <Lightbulb className="w-3.5 h-3.5 shrink-0 text-amber-400" />
          <span className="italic">{suggestion.tactical_tip}</span>
        </div>
      )}
    </div>
  );
};
