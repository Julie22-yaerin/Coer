import React, { useState } from "react";
import { UserCheck, Save } from "lucide-react";
import { FounderProfile } from "../../types/coer";

interface ProfileEditorProps {
  initialProfile?: FounderProfile | null;
  onSaveProfile: (profile: Partial<FounderProfile>) => Promise<void>;
}

export const ProfileEditor: React.FC<ProfileEditorProps> = ({
  initialProfile,
  onSaveProfile,
}) => {
  const [name, setName] = useState(initialProfile?.name || "");
  const [role, setRole] = useState(initialProfile?.role || "");
  const [vision, setVision] = useState(initialProfile?.vision_statement || "");
  const [isSaving, setIsSaving] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      await onSaveProfile({
        name,
        role,
        vision_statement: vision,
      });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-4 p-5 rounded-2xl bg-neutral-900/60 border border-white/10 text-white"
    >
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold tracking-wide text-neutral-200 flex items-center gap-2">
          <UserCheck className="w-4 h-4 text-emerald-400" />
          <span>Founder Baseline Profile</span>
        </h3>
        <span className="text-[10px] text-neutral-500 font-mono">Used for FCI matching</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div className="flex flex-col gap-1">
          <label className="text-xs text-neutral-400">Founder Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. Alex Chen"
            className="text-xs bg-neutral-800/80 border border-white/10 rounded-xl px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
            required
          />
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-xs text-neutral-400">Current Role</label>
          <input
            type="text"
            value={role}
            onChange={(e) => setRole(e.target.value)}
            placeholder="e.g. Technical CEO"
            className="text-xs bg-neutral-800/80 border border-white/10 rounded-xl px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
            required
          />
        </div>
      </div>

      <div className="flex flex-col gap-1">
        <label className="text-xs text-neutral-400">Company Vision & Culture Baseline</label>
        <textarea
          rows={3}
          value={vision}
          onChange={(e) => setVision(e.target.value)}
          placeholder="Describe your 5-year mission, core values, and non-negotiables..."
          className="text-xs bg-neutral-800/80 border border-white/10 rounded-xl px-3 py-2 text-white focus:outline-none focus:border-emerald-500 resize-none"
          required
        />
      </div>

      <button
        type="submit"
        disabled={isSaving}
        className="self-end flex items-center gap-2 text-xs font-medium px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white transition-colors disabled:opacity-50"
      >
        <Save className="w-3.5 h-3.5" />
        <span>{isSaving ? "Saving..." : "Save Baseline"}</span>
      </button>
    </form>
  );
};
