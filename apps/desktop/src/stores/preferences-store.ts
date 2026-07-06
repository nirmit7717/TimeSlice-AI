import { create } from "zustand";
import { persist } from "zustand/middleware";

export type Theme = "dark" | "light" | "system";
export type SidebarState = "expanded" | "collapsed";

interface Preferences {
  // UI
  theme: Theme;
  sidebarState: SidebarState;
  showKernelPanel: boolean;

  // Scheduling constraints
  workStartTime: string;
  workEndTime: string;
  focusStartTime: string;
  focusEndTime: string;
  restStartTime: string;
  restEndTime: string;
  maxSessionMinutes: number;
  minBreakMinutes: number;
  maxDailyFocusHours: number;
  contextSwitchPenaltyMinutes: number;

  // Constraint rules
  respectCalendarEvents: boolean;
  allowWeekends: boolean;
  enforceRestPeriods: boolean;
  adaptiveQuantum: boolean;

  // Scheduling policy
  activePolicy: string;

  // Last visited route
  lastRoute: string;
}

interface PreferencesStore extends Preferences {
  setTheme: (theme: Theme) => void;
  setSidebarState: (state: SidebarState) => void;
  setShowKernelPanel: (show: boolean) => void;
  setWorkHours: (start: string, end: string) => void;
  setFocusWindow: (start: string, end: string) => void;
  setRestPeriod: (start: string, end: string) => void;
  setMaxSession: (minutes: number) => void;
  setMinBreak: (minutes: number) => void;
  setMaxDailyFocus: (hours: number) => void;
  setContextSwitchPenalty: (minutes: number) => void;
  setConstraintRule: (key: keyof Pick<Preferences, "respectCalendarEvents" | "allowWeekends" | "enforceRestPeriods" | "adaptiveQuantum">, value: boolean) => void;
  setActivePolicy: (policy: string) => void;
  setLastRoute: (route: string) => void;
  resetToDefaults: () => void;
}

const defaults: Preferences = {
  theme: "dark",
  sidebarState: "expanded",
  showKernelPanel: true,
  workStartTime: "09:00",
  workEndTime: "18:00",
  focusStartTime: "09:00",
  focusEndTime: "12:00",
  restStartTime: "12:00",
  restEndTime: "13:00",
  maxSessionMinutes: 90,
  minBreakMinutes: 15,
  maxDailyFocusHours: 6,
  contextSwitchPenaltyMinutes: 30,
  respectCalendarEvents: true,
  allowWeekends: false,
  enforceRestPeriods: true,
  adaptiveQuantum: true,
  activePolicy: "priority",
  lastRoute: "/",
};

export const usePreferencesStore = create<PreferencesStore>()(
  persist(
    (set) => ({
      ...defaults,

      setTheme: (theme) => set({ theme }),
      setSidebarState: (sidebarState) => set({ sidebarState }),
      setShowKernelPanel: (showKernelPanel) => set({ showKernelPanel }),
      setWorkHours: (start, end) =>
        set({ workStartTime: start, workEndTime: end }),
      setFocusWindow: (start, end) =>
        set({ focusStartTime: start, focusEndTime: end }),
      setRestPeriod: (start, end) =>
        set({ restStartTime: start, restEndTime: end }),
      setMaxSession: (maxSessionMinutes) => set({ maxSessionMinutes }),
      setMinBreak: (minBreakMinutes) => set({ minBreakMinutes }),
      setMaxDailyFocus: (maxDailyFocusHours) => set({ maxDailyFocusHours }),
      setContextSwitchPenalty: (contextSwitchPenaltyMinutes) =>
        set({ contextSwitchPenaltyMinutes }),
      setConstraintRule: (key, value) => set({ [key]: value }),
      setActivePolicy: (activePolicy) => set({ activePolicy }),
      setLastRoute: (lastRoute) => set({ lastRoute }),
      resetToDefaults: () => set(defaults),
    }),
    {
      name: "timeslice-preferences",
    }
  )
);
