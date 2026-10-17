import React from "react";
import { Users, Clock, CheckCircle, ArrowRight } from "lucide-react";
import { MeetingSession } from "../../types/coer";

interface SessionListProps {
  sessions: MeetingSession[];
  onSelectSession: (sessionId: string) => void;
  selectedSessionId?: string | null;
}

export const SessionList: React.FC<SessionListProps> = ({
  sessions,
  onSelectSession,
  selectedSessionId,
}) => {
  return (
    <div className="flex flex-col gap-3 p-5 rounded-2xl bg-neutral-900/60 border border-white/10 text-white">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold tracking-wide text-neutral-200 flex items-center gap-2">
          <Users className="w-4 h-4 text-emerald-400" />
          <span>Meeting History & Interviews</span>
        </h3>
        <span className="text-xs text-neutral-500 font-mono">{sessions.length} calls</span>
      </div>

      <div className="flex flex-col gap-2">
        {sessions.length === 0 ? (
          <div className="text-xs text-neutral-500 py-6 text-center">
            No previous meeting sessions found.
          </div>
        ) : (
          sessions.map((s) => {
            const isSelected = s.id === selectedSessionId;
            return (
              <button
                key={s.id}
                onClick={() => onSelectSession(s.id)}
                className={`flex items-center justify-between p-3 rounded-xl border text-left transition-all ${
                  isSelected
                    ? "bg-white/10 border-emerald-500/50 shadow-lg"
                    : "bg-white/5 border-white/5 hover:bg-white/10"
                }`}
              >
                <div className="flex flex-col gap-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-white">{s.candidate_name}</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/10 text-neutral-300 font-medium">
                      {s.target_role}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 text-[10px] text-neutral-500">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {new Date(s.started_at).toLocaleDateString()}
                    </span>
                    {s.total_duration_sec && (
                      <span>{Math.round(s.total_duration_sec / 60)} mins</span>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span
                    className={`text-[10px] font-medium px-2 py-0.5 rounded-full ${
                      s.status === "COMPLETED"
                        ? "text-emerald-400 bg-emerald-500/10"
                        : "text-amber-400 bg-amber-500/10"
                    }`}
                  >
                    {s.status}
                  </span>
                  <ArrowRight className="w-3.5 h-3.5 text-neutral-500" />
                </div>
              </button>
            );
          })
        )}
      </div>
    </div>
  );
};
