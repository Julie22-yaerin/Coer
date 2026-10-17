import React from "react";
import { Award, CheckCircle2, TrendingUp } from "lucide-react";

interface MatchIndexProps {
  score: number; // 0 - 100
  candidateName: string;
  targetRole: string;
}

export const MatchIndex: React.FC<MatchIndexProps> = ({
  score,
  candidateName,
  targetRole,
}) => {
  const getBadgeColor = (val: number) => {
    if (val >= 80) return "text-emerald-400 bg-emerald-500/10 border-emerald-500/30";
    if (val >= 65) return "text-blue-400 bg-blue-500/10 border-blue-500/30";
    return "text-amber-400 bg-amber-500/10 border-amber-500/30";
  };

  const getAssessmentText = (val: number) => {
    if (val >= 85) return "Exceptional Complementarity — High probability of long-term co-founder synergy.";
    if (val >= 70) return "Strong Compatibility — Complementary skills with healthy operational tension.";
    if (val >= 50) return "Moderate Fit — Areas of friction detected around execution or vision alignment.";
    return "Low Compatibility — Substantial divergent motivations or communication misalignment.";
  };

  return (
    <div className="flex flex-col gap-4 p-5 rounded-2xl bg-neutral-900/60 border border-white/10 text-white">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Award className="w-5 h-5 text-emerald-400" />
          <h3 className="text-sm font-semibold tracking-wide text-neutral-200">
            Founder Complementarity Index (FCI)
          </h3>
        </div>
        <span
          className={`text-xs px-2.5 py-1 rounded-full border font-mono font-bold ${getBadgeColor(
            score
          )}`}
        >
          {score} / 100
        </span>
      </div>

      <div className="flex items-baseline gap-3">
        <span className="text-4xl font-extrabold font-mono tracking-tight text-white">
          {score}%
        </span>
        <div className="text-xs text-neutral-400">
          Target role: <span className="text-white font-medium">{targetRole}</span> for candidate{" "}
          <span className="text-white font-medium">{candidateName}</span>
        </div>
      </div>

      <p className="text-xs text-neutral-300 leading-relaxed bg-white/5 p-3 rounded-xl border border-white/5">
        {getAssessmentText(score)}
      </p>
    </div>
  );
};
