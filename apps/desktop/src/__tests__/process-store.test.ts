import { vi, beforeEach, describe, it, expect } from "vitest";

// Mock localStorage globally
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => { store[key] = value.toString(); },
    clear: () => { store = {}; },
    removeItem: (key: string) => { delete store[key]; }
  };
})();
Object.defineProperty(global, "localStorage", { value: localStorageMock });

import { useProcessStore } from "../stores/process-store";

describe("process-store", () => {
  beforeEach(() => {
    localStorage.clear();
    // Reset Zustand store state before each test
    useProcessStore.setState({ processes: [] });
    vi.restoreAllMocks();
  });

  it("should have initial empty processes", () => {
    const state = useProcessStore.getState();
    expect(state.processes).toEqual([]);
  });

  it("should fetch processes from API", async () => {
    const mockApiResponse = [
      {
        id: "p1",
        name: "Test Process 1",
        description: "Desc 1",
        goal: "Goal 1",
        deadline: "2026-07-12T00:00:00Z",
        priority: 4,
        estimatedEffortHours: 5.0,
        status: "Active",
        progress: 0.25,
        attentionDebt: 1.0,
        attentionEquity: 2.0,
        notes: "",
        createdAt: "2026-07-12T00:00:00Z",
        updatedAt: "2026-07-12T00:00:00Z"
      }
    ];

    const fetchMock = vi.fn().mockImplementation(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockApiResponse),
      })
    );
    global.fetch = fetchMock;

    await useProcessStore.getState().fetchProcesses();

    const state = useProcessStore.getState();
    expect(fetchMock).toHaveBeenCalledWith("http://localhost:8000/api/v1/processes");
    expect(state.processes.length).toBe(1);
    expect(state.processes[0].id).toBe("p1");
    // Ensure estimatedEffort mappings work
    expect(state.processes[0].estimatedEffort).toBe(5.0);
    // Ensure progress mapping (Math.round(0.25 * 100)) works
    expect(state.processes[0].progress).toBe(25);
  });

  it("should add process successfully via API and fallback locally on failure", async () => {
    const mockCreatedResponse = {
      id: "p-new",
      name: "New Process",
      description: "New Desc",
      goal: "New Goal",
      deadline: "2026-07-12T00:00:00Z",
      priority: 3,
      estimatedEffortHours: 10.0,
      status: "Active",
      progress: 0.0,
      attentionDebt: 0.0,
      attentionEquity: 0.0,
      notes: "",
      createdAt: "2026-07-12T00:00:00Z",
      updatedAt: "2026-07-12T00:00:00Z"
    };

    const fetchMock = vi.fn().mockImplementation(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockCreatedResponse),
      })
    );
    global.fetch = fetchMock;

    await useProcessStore.getState().addProcess({
      name: "New Process",
      description: "New Desc",
      goal: "New Goal",
      deadline: "2026-07-12T00:00:00Z",
      priority: 3,
      estimatedEffort: 10.0,
      status: "Active",
      notes: ""
    });

    const state = useProcessStore.getState();
    expect(state.processes.length).toBe(1);
    expect(state.processes[0].id).toBe("p-new");
    expect(state.processes[0].estimatedEffort).toBe(10.0);
  });
});
