import { create } from "zustand";

interface OperatorModel {
  focus_duration_avg: number;
  switch_tolerance: number;
  consistency_score: number;
  velocity_score: number;
  total_slices_completed: number;
  total_slices_abandoned: number;
  completion_rate: number;
}

interface AdaptiveProfile {
  preferred_policy: string;
  preferred_quantum_hours: number;
  working_hours_start: number;
  working_hours_end: number;
  max_daily_hours: number;
  telegram_chat_id?: string | null;
  telegram_connected?: boolean;
  local_notifications?: boolean;
  last_updated: string | null;
}

interface AdaptiveStore {
  profile: AdaptiveProfile | null;
  operatorModel: OperatorModel | null;
  isLoading: boolean;
  error: string | null;

  fetchProfile: () => Promise<void>;
  fetchOperatorModel: () => Promise<void>;
  overrideProfile: (overrides: Partial<AdaptiveProfile>) => Promise<void>;
}

const API_BASE = "http://127.0.0.1:8000/api/v1/adaptive";

export const useAdaptiveStore = create<AdaptiveStore>((set) => ({
  profile: null,
  operatorModel: null,
  isLoading: false,
  error: null,

  fetchProfile: async () => {
    set({ isLoading: true, error: null });
    try {
      const res = await fetch(`${API_BASE}/profile`);
      if (!res.ok) throw new Error("Failed to fetch adaptive profile");
      const data = await res.json();
      set({ profile: data, isLoading: false });
    } catch (err) {
      set({ error: String(err), isLoading: false });
    }
  },

  fetchOperatorModel: async () => {
    set({ isLoading: true, error: null });
    try {
      const res = await fetch(`${API_BASE}/operator-model`);
      if (!res.ok) throw new Error("Failed to fetch operator model");
      const data = await res.json();
      set({ operatorModel: data, isLoading: false });
    } catch (err) {
      set({ error: String(err), isLoading: false });
    }
  },

  overrideProfile: async (overrides) => {
    set({ isLoading: true, error: null });
    try {
      const res = await fetch(`${API_BASE}/profile`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(overrides),
      });
      if (!res.ok) throw new Error("Failed to update adaptive profile");
      const data = await res.json();
      set({ profile: data, isLoading: false });
    } catch (err) {
      set({ error: String(err), isLoading: false });
    }
  },
}));
