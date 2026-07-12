import { create } from "zustand";

export interface CalendarEvent {
  id: string;
  title: string;
  start_time: string;
  end_time: string;
  description: string;
  location: string;
  is_google_event: boolean;
  is_rest_period: boolean;
  color: string;
  source: "local" | "google" | "execution_plan";
}

interface CalendarStore {
  events: CalendarEvent[];
  isLoading: boolean;
  error: string | null;
  googleSyncStatus: { status: string; message: string; auth_url?: string } | null;

  fetchEvents: (start?: string, end?: string) => Promise<void>;
  createEvent: (event: Omit<CalendarEvent, "id" | "is_google_event" | "source">) => Promise<void>;
  updateEvent: (id: string, event: Partial<CalendarEvent>) => Promise<void>;
  deleteEvent: (id: string) => Promise<void>;
  getGoogleAuthUrl: () => Promise<void>;
  syncGoogleCalendar: () => Promise<void>;
}

const API_BASE = "http://127.0.0.1:8000/api/v1/calendar";

export const useCalendarStore = create<CalendarStore>((set) => ({
  events: [],
  isLoading: false,
  error: null,
  googleSyncStatus: null,

  fetchEvents: async (start, end) => {
    set({ isLoading: true, error: null });
    try {
      let url = `${API_BASE}/events`;
      const params = new URLSearchParams();
      if (start) params.append("start", start);
      if (end) params.append("end", end);
      if (params.toString()) url += `?${params.toString()}`;

      const res = await fetch(url);
      if (!res.ok) throw new Error("Failed to fetch calendar events");
      const data = await res.json();
      set({ events: data, isLoading: false });
    } catch (err) {
      set({ error: String(err), isLoading: false });
    }
  },

  createEvent: async (event) => {
    set({ isLoading: true, error: null });
    try {
      const res = await fetch(`${API_BASE}/events`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(event),
      });
      if (!res.ok) throw new Error("Failed to create calendar event");
      const newEvent = await res.json();
      set((state) => ({
        events: [...state.events, newEvent].sort((a, b) => a.start_time.localeCompare(b.start_time)),
        isLoading: false,
      }));
    } catch (err) {
      set({ error: String(err), isLoading: false });
    }
  },

  updateEvent: async (id, event) => {
    set({ isLoading: true, error: null });
    try {
      const res = await fetch(`${API_BASE}/events/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(event),
      });
      if (!res.ok) throw new Error("Failed to update calendar event");
      const updatedEvent = await res.json();
      set((state) => ({
        events: state.events.map((e) => (e.id === id ? updatedEvent : e)),
        isLoading: false,
      }));
    } catch (err) {
      set({ error: String(err), isLoading: false });
    }
  },

  deleteEvent: async (id) => {
    set({ isLoading: true, error: null });
    try {
      const res = await fetch(`${API_BASE}/events/${id}`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error("Failed to delete calendar event");
      set((state) => ({
        events: state.events.filter((e) => e.id !== id),
        isLoading: false,
      }));
    } catch (err) {
      set({ error: String(err), isLoading: false });
    }
  },

  getGoogleAuthUrl: async () => {
    try {
      const res = await fetch(`${API_BASE}/google/auth-url`);
      if (res.ok) {
        const data = await res.json();
        set({ googleSyncStatus: data });
      }
    } catch (err) {
      console.error("Failed to fetch Google auth URL:", err);
    }
  },

  syncGoogleCalendar: async () => {
    set({ isLoading: true });
    try {
      const res = await fetch(`${API_BASE}/sync/google`, { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        set({ googleSyncStatus: data, isLoading: false });
      }
    } catch (err) {
      set({ error: String(err), isLoading: false });
    }
  },
}));
