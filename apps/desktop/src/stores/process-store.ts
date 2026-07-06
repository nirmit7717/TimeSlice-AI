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

interface ProcessStore {
  processes: Process[];
  addProcess: (process: Omit<Process, "id" | "createdAt" | "updatedAt" | "progress" | "attentionDebt" | "attentionEquity">) => void;
  updateProcess: (id: string, updates: Partial<Process>) => void;
  deleteProcess: (id: string) => void;
  pauseProcess: (id: string) => void;
  resumeProcess: (id: string) => void;
  archiveProcess: (id: string) => void;
  getProcessById: (id: string) => Process | undefined;
}

const initialProcesses: Process[] = [
  {
    id: "proc-1",
    name: "Backend Scheduler API",
    description: "Build the core scheduling engine REST API",
    goal: "Complete all CRUD endpoints and policy execution",
    deadline: "2026-07-10",
    priority: 5,
    estimatedEffort: 40,
    status: "Active",
    progress: 65,
    attentionDebt: 3.2,
    attentionEquity: 12.5,
    notes: "Focus on Round Robin and Priority policies first",
    createdAt: "2026-06-15T10:00:00Z",
    updatedAt: "2026-07-06T18:30:00Z",
  },
  {
    id: "proc-2",
    name: "Azure AZ-900 Certification",
    description: "Study for Azure Fundamentals certification exam",
    goal: "Pass AZ-900 exam with 80%+ score",
    deadline: "2026-07-15",
    priority: 4,
    estimatedEffort: 25,
    status: "Active",
    progress: 28,
    attentionDebt: 5.1,
    attentionEquity: 6.8,
    notes: "Complete modules on compute, networking, and storage",
    createdAt: "2026-06-20T09:00:00Z",
    updatedAt: "2026-07-05T14:00:00Z",
  },
  {
    id: "proc-3",
    name: "Q4 Planning Review",
    description: "Quarterly planning document and roadmap review",
    goal: "Finalize Q4 objectives and resource allocation",
    deadline: "2026-07-20",
    priority: 3,
    estimatedEffort: 10,
    status: "Paused",
    progress: 12,
    attentionDebt: 8.5,
    attentionEquity: 1.2,
    notes: "Waiting for team input on budget allocations",
    createdAt: "2026-06-25T11:00:00Z",
    updatedAt: "2026-07-01T16:00:00Z",
  },
  {
    id: "proc-4",
    name: "Code Review Session",
    description: "Review outstanding PRs and provide feedback",
    goal: "Clear PR backlog and document patterns",
    deadline: "2026-07-09",
    priority: 4,
    estimatedEffort: 5,
    status: "Active",
    progress: 45,
    attentionDebt: 1.5,
    attentionEquity: 3.0,
    notes: "",
    createdAt: "2026-07-01T08:00:00Z",
    updatedAt: "2026-07-06T20:00:00Z",
  },
  {
    id: "proc-5",
    name: "Personal Portfolio",
    description: "Build and deploy personal portfolio website",
    goal: "Launch portfolio with 5 case studies",
    deadline: "2026-08-01",
    priority: 2,
    estimatedEffort: 30,
    status: "Completed",
    progress: 100,
    attentionDebt: 0,
    attentionEquity: 30,
    notes: "Deployed at portfolio.dev",
    createdAt: "2026-05-01T10:00:00Z",
    updatedAt: "2026-06-28T12:00:00Z",
  },
];

export const useProcessStore = create<ProcessStore>()(
  persist(
    (set, get) => ({
      processes: initialProcesses,

      addProcess: (processData) => {
        const now = new Date().toISOString();
        const newProcess: Process = {
          ...processData,
          id: `proc-${Date.now()}`,
          progress: 0,
          attentionDebt: 0,
          attentionEquity: 0,
          createdAt: now,
          updatedAt: now,
        };
        set((state) => ({ processes: [...state.processes, newProcess] }));
      },

      updateProcess: (id, updates) => {
        set((state) => ({
          processes: state.processes.map((p) =>
            p.id === id ? { ...p, ...updates, updatedAt: new Date().toISOString() } : p
          ),
        }));
      },

      deleteProcess: (id) => {
        set((state) => ({
          processes: state.processes.filter((p) => p.id !== id),
        }));
      },

      pauseProcess: (id) => {
        set((state) => ({
          processes: state.processes.map((p) =>
            p.id === id ? { ...p, status: "Paused" as ProcessStatus, updatedAt: new Date().toISOString() } : p
          ),
        }));
      },

      resumeProcess: (id) => {
        set((state) => ({
          processes: state.processes.map((p) =>
            p.id === id ? { ...p, status: "Active" as ProcessStatus, updatedAt: new Date().toISOString() } : p
          ),
        }));
      },

      archiveProcess: (id) => {
        set((state) => ({
          processes: state.processes.map((p) =>
            p.id === id ? { ...p, status: "Archived" as ProcessStatus, updatedAt: new Date().toISOString() } : p
          ),
        }));
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
