import React from "react";
import { Quote, AlertTriangle, CheckCircle2 } from "lucide-react";
import { EvidenceCitation } from "../../types/coer";

interface EvidenceListProps {
  citations: EvidenceCitation[];
  strengths: string[];
  redFlags: string[];
}

export const EvidenceList: React.FC<EvidenceListProps> = ({
  citations,
  strengths,
  redFlags,
}) => {
  return (
    <div className="flex flex-col gap-5 p-5 rounded-2xl bg-neutral-900/60 border border-white/10 text-white">
      {/* Strengths & Red Flags */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Strengths */}
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-400">
            <CheckCircle2 className="w-4 h-4" />
            <span>Observed Strengths</span>
          </div>
          <ul className="flex flex-col gap-1.5">
            {strengths.map((str, idx) => (
              <li
                key={idx}
                className="text-xs text-neutral-300 bg-emerald-500/5 border border-emerald-500/10 p-2 rounded-lg"
              >
                {str}
              </li>
            ))}
          </ul>
        </div>

        {/* Red Flags / Risk Points */}
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-rose-400">
            <AlertTriangle className="w-4 h-4" />
            <span>Risk Factors & Nuance</span>
          </div>
          <ul className="flex flex-col gap-1.5">
            {redFlags.map((rf, idx) => (
              <li
                key={idx}
                className="text-xs text-neutral-300 bg-rose-500/5 border border-rose-500/10 p-2 rounded-lg"
              >
                {rf}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Timestamped Transcript Citations */}
      <div className="flex flex-col gap-3 mt-2">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-neutral-200">
          <Quote className="w-4 h-4 text-neutral-400" />
          <span>Timestamped Transcript Evidence</span>
        </div>

        <div className="flex flex-col gap-2">
          {citations.length === 0 ? (
            <p className="text-xs text-neutral-500 italic">No specific dialogue quotes cited.</p>
          ) : (
            citations.map((c, idx) => (
              <div
                key={idx}
                className="flex flex-col gap-1 text-xs bg-white/5 border border-white/5 p-3 rounded-xl"
              >
                <div className="flex items-center justify-between text-[11px] text-neutral-400">
                  <span className="font-semibold text-neutral-200">{c.trait}</span>
                  <span className="font-mono text-emerald-400">[{c.timestamp}]</span>
                </div>
                <p className="text-neutral-200 italic font-serif">"{c.quote}"</p>
                <p className="text-[11px] text-neutral-400">{c.reasoning}</p>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
