import { vi, beforeEach, describe, it, expect } from "vitest";

import { useCalendarStore } from "../stores/calendar-store";

describe("calendar-store", () => {
  beforeEach(() => {
    useCalendarStore.setState({
      events: [],
      isLoading: false,
      error: null,
      googleSyncStatus: null,
    });
    vi.restoreAllMocks();
  });

  it("should have initial state", () => {
    const state = useCalendarStore.getState();
    expect(state.events).toEqual([]);
    expect(state.isLoading).toBe(false);
  });

  it("should fetch calendar events", async () => {
    const mockEvents = [
      {
        id: "evt-1",
        title: "Test Event 1",
        start_time: "2026-07-12T10:00:00Z",
        end_time: "2026-07-12T11:00:00Z",
        description: "Desc",
        location: "Loc",
        is_google_event: false,
        is_rest_period: false,
        color: "blue",
        source: "local",
      },
    ];

    const fetchMock = vi.fn().mockImplementation(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockEvents),
      })
    );
    global.fetch = fetchMock;

    await useCalendarStore.getState().fetchEvents();

    const state = useCalendarStore.getState();
    expect(state.events.length).toBe(1);
    expect(state.events[0].id).toBe("evt-1");
  });

  it("should handle sync error", async () => {
    const fetchMock = vi.fn().mockImplementation(() =>
      Promise.reject(new Error("Network Error"))
    );
    global.fetch = fetchMock;

    await useCalendarStore.getState().fetchEvents();

    const state = useCalendarStore.getState();
    expect(state.error).toBe("Error: Network Error");
    expect(state.isLoading).toBe(false);
  });
});
