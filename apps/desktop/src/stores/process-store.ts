import { create } from "zustand";
import { persist } from "zustand/middleware";

export type ProcessStatus = "Active" | "Paused" | "Completed" | "Archived";

export interface Process {
  id: string;
  name: string;
  description: string;
  goal: string;
  deadline: string;
  priority: number;
  estimatedEffort: number; // hours
  status: ProcessStatus;
  progress: number;
  attentionDebt: number; // hours
  attentionEquity: number; // hours
  notes: string;
  createdAt: string;
  updatedAt: string;
}

const API_BASE_URL = "http://localhost:8000/api/v1";

interface ProcessStore {
  processes: Process[];
  fetchProcesses: () => Promise<void>;
  addProcess: (process: Omit<Process, "id" | "createdAt" | "updatedAt" | "progress" | "attentionDebt" | "attentionEquity">) => Promise<void>;
  updateProcess: (id: string, updates: Partial<Process>) => Promise<void>;
  deleteProcess: (id: string) => Promise<void>;
  pauseProcess: (id: string) => Promise<void>;
  resumeProcess: (id: string) => Promise<void>;
  archiveProcess: (id: string) => Promise<void>;
  getProcessById: (id: string) => Process | undefined;
}

const initialProcesses: Process[] = [];

export const useProcessStore = create<ProcessStore>()(
  persist(
    (set, get) => ({
      processes: initialProcesses,

      fetchProcesses: async () => {
        try {
          const res = await fetch(`${API_BASE_URL}/processes`);
          if (res.ok) {
            const data = await res.json();
            const mapped = data.map((p: any) => ({
              ...p,
              estimatedEffort: p.estimatedEffortHours || 0,
              progress: Math.round((p.progress || 0) * 100),
            }));
            set({ processes: mapped });
          }
        } catch (err) {
          console.warn("Backend API offline, using local cache:", err);
        }
      },

      addProcess: async (processData) => {
        try {
          const payload = {
            name: processData.name,
            description: processData.description,
            goal: processData.goal,
            deadline: processData.deadline,
            priority: processData.priority,
            estimatedEffortHours: processData.estimatedEffort,
            status: processData.status,
            tags: [],
          };
          const res = await fetch(`${API_BASE_URL}/processes`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          });
          if (res.ok) {
            const data = await res.json();
            const newProcess: Process = {
              ...data,
              estimatedEffort: data.estimatedEffortHours,
              progress: Math.round((data.progress || 0) * 100),
            };
            set((state) => ({ processes: [...state.processes, newProcess] }));
            return;
          }
        } catch (err) {
          console.error("Backend offline, saving locally:", err);
        }
        
        // Local fallback
        const now = new Date().toISOString();
        const localProcess: Process = {
          ...processData,
          id: `proc-${Date.now()}`,
          progress: 0,
          attentionDebt: 0,
          attentionEquity: 0,
          notes: "",
          createdAt: now,
          updatedAt: now,
        };
        set((state) => ({ processes: [...state.processes, localProcess] }));
      },

      updateProcess: async (id, updates) => {
        try {
          const payload: any = {};
          if (updates.name !== undefined) payload.name = updates.name;
          if (updates.description !== undefined) payload.description = updates.description;
          if (updates.goal !== undefined) payload.goal = updates.goal;
          if (updates.deadline !== undefined) payload.deadline = updates.deadline;
          if (updates.priority !== undefined) payload.priority = updates.priority;
          if (updates.estimatedEffort !== undefined) payload.estimatedEffortHours = updates.estimatedEffort;
          if (updates.status !== undefined) payload.status = updates.status;
          if (updates.progress !== undefined) payload.progress = updates.progress / 100;

          const res = await fetch(`${API_BASE_URL}/processes/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          });
          if (res.ok) {
            const data = await res.json();
            const updatedProcess: Process = {
              ...data,
              estimatedEffort: data.estimatedEffortHours,
              progress: Math.round((data.progress || 0) * 100),
            };
            set((state) => ({
              processes: state.processes.map((p) => (p.id === id ? updatedProcess : p)),
            }));
            return;
          }
        } catch (err) {
          console.error("Backend offline, updating locally:", err);
        }

        set((state) => ({
          processes: state.processes.map((p) =>
            p.id === id ? { ...p, ...updates, updatedAt: new Date().toISOString() } : p
          ),
        }));
      },

      deleteProcess: async (id) => {
        try {
          const res = await fetch(`${API_BASE_URL}/processes/${id}`, { method: "DELETE" });
          if (res.ok) {
            set((state) => ({ processes: state.processes.filter((p) => p.id !== id) }));
            return;
          }
        } catch (err) {
          console.error("Backend offline, deleting locally:", err);
        }
        set((state) => ({ processes: state.processes.filter((p) => p.id !== id) }));
      },

      pauseProcess: async (id) => {
        const store = get();
        await store.updateProcess(id, { status: "Paused" as ProcessStatus });
      },

      resumeProcess: async (id) => {
        const store = get();
        await store.updateProcess(id, { status: "Active" as ProcessStatus });
      },

      archiveProcess: async (id) => {
        const store = get();
        await store.updateProcess(id, { status: "Archived" as ProcessStatus });
      },

      getProcessById: (id) => {
        return get().processes.find((p) => p.id === id);
      },
    }),
    {
      name: "timeslice-processes",
    }
  )
);
