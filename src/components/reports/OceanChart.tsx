import React from "react";

interface OceanChartProps {
  scores: {
    ocean_openness: number;
    ocean_conscientiousness: number;
    ocean_extraversion: number;
    ocean_agreeableness: number;
    ocean_neuroticism: number;
  };
}

const TRAIT_CONFIG = [
  { key: "ocean_openness", label: "Openness", desc: "Innovation & ambiguity tolerance", color: "bg-blue-500" },
  { key: "ocean_conscientiousness", label: "Conscientiousness", desc: "Execution rigor & operational discipline", color: "bg-emerald-500" },
  { key: "ocean_extraversion", label: "Extraversion", desc: "Pitching comfort & communication energy", color: "bg-purple-500" },
  { key: "ocean_agreeableness", label: "Agreeableness", desc: "Pragmatic negotiation & team empathy", color: "bg-amber-500" },
  { key: "ocean_neuroticism", label: "Emotional Stability", desc: "Stress resilience under startup chaos", color: "bg-rose-500", invert: true },
];

export const OceanChart: React.FC<OceanChartProps> = ({ scores }) => {
  return (
    <div className="flex flex-col gap-4 p-5 rounded-2xl bg-neutral-900/60 border border-white/10 text-white">
      <h3 className="text-sm font-semibold tracking-wide text-neutral-200">
        OCEAN Big Five Personality Dimensions
      </h3>

      <div className="flex flex-col gap-3.5">
        {TRAIT_CONFIG.map(({ key, label, desc, color, invert }) => {
          const raw = scores[key as keyof typeof scores] || 50;
          const displayScore = invert ? Math.round(100 - raw) : Math.round(raw);

          return (
            <div key={key} className="flex flex-col gap-1">
              <div className="flex items-center justify-between text-xs">
                <span className="font-medium text-neutral-200">{label}</span>
                <span className="font-mono text-neutral-400">{displayScore}/100</span>
              </div>
              <div className="w-full h-2 bg-neutral-800 rounded-full overflow-hidden">
                <div
                  className={`h-full ${color} rounded-full transition-all duration-700 ease-out`}
                  style={{ width: `${displayScore}%` }}
                />
              </div>
              <span className="text-[10px] text-neutral-500">{desc}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
