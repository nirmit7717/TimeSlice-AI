import { ChevronLeft, ChevronRight, Sparkles } from "lucide-react";
import { useState } from "react";
import { useProcessStore } from "../stores/process-store";
import { usePreferencesStore } from "../stores/preferences-store";

interface CalendarEvent {
  id: string;
  title: string;
  time: string;
  duration: number; // in hours
  color: string;
}

const mockEvents: Record<string, CalendarEvent[]> = {
  "2026-07-07": [
    { id: "1", title: "Backend Scheduler", time: "09:00", duration: 1.5, color: "bg-primary" },
    { id: "2", title: "Azure AZ-900", time: "11:00", duration: 2, color: "bg-secondary" },
    { id: "3", title: "Gym", time: "15:00", duration: 1, color: "bg-emerald-500" },
    { id: "4", title: "Research", time: "20:00", duration: 1.5, color: "bg-amber-500" },
  ],
  "2026-07-08": [
    { id: "5", title: "Code Review", time: "10:00", duration: 1, color: "bg-primary" },
    { id: "6", title: "Q4 Planning", time: "14:00", duration: 2, color: "bg-amber-500" },
  ],
  "2026-07-09": [
    { id: "7", title: "Backend Scheduler", time: "09:00", duration: 2, color: "bg-primary" },
    { id: "8", title: "Azure AZ-900", time: "16:00", duration: 1.5, color: "bg-secondary" },
  ],
  "2026-07-10": [
    { id: "9", title: "Backend Scheduler", time: "08:00", duration: 2, color: "bg-primary" },
    { id: "10", title: "Gym", time: "12:00", duration: 1, color: "bg-emerald-500" },
    { id: "11", title: "Research", time: "19:00", duration: 2, color: "bg-amber-500" },
  ],
  "2026-07-11": [
    { id: "12", title: "Code Review", time: "09:00", duration: 1, color: "bg-primary" },
  ],
};

const hours = Array.from({ length: 14 }, (_, i) => i + 7); // 7AM to 8PM
const dayNames = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

function getWeekDates(baseDate: Date): Date[] {
  const start = new Date(baseDate);
  const day = start.getDay();
  const diff = day === 0 ? -6 : 1 - day; // Monday start
  start.setDate(start.getDate() + diff);
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(start);
    d.setDate(start.getDate() + i);
    return d;
  });
}

function formatDateKey(date: Date): string {
  return date.toISOString().split("T")[0];
}

export function CalendarPage() {
  const processes = useProcessStore((s) => s.processes);
  const activePolicy = usePreferencesStore((s) => s.activePolicy);
  const maxDailyFocusHours = usePreferencesStore((s) => s.maxDailyFocusHours);

  const [currentDate, setCurrentDate] = useState(new Date("2026-07-07"));
  const [events, setEvents] = useState<Record<string, CalendarEvent[]>>(mockEvents);
  const [isOptimizing, setIsOptimizing] = useState(false);

  const weekDates = getWeekDates(currentDate);

  const goToPrevWeek = () => {
    const d = new Date(currentDate);
    d.setDate(d.getDate() - 7);
    setCurrentDate(d);
  };

  const goToNextWeek = () => {
    const d = new Date(currentDate);
    d.setDate(d.getDate() + 7);
    setCurrentDate(d);
  };

  const handleOptimizePlan = async () => {
    setIsOptimizing(true);
    try {
      const payload = {
        policyName: activePolicy.charAt(0).toUpperCase() + activePolicy.slice(1), // format e.g. "Priority"
        availableHours: maxDailyFocusHours,
        quantumHours: 2.0,
        blockedIntervals: []
      };

      const res = await fetch("http://localhost:8000/api/v1/scheduler/plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const data = await res.json();
        const newEvents: Record<string, CalendarEvent[]> = {};

        data.executionWindows.forEach((w: any) => {
          const ts = w.timeSlice;
          const start = new Date(ts.startTime);
          const dateKey = start.toISOString().split("T")[0];
          const timeStr = start.toTimeString().substring(0, 5);
          const duration = ts.durationHours;
          const proc = processes.find((p) => p.id === ts.processId);
          const title = proc ? proc.name : "Scheduled Slot";

          if (!newEvents[dateKey]) {
            newEvents[dateKey] = [];
          }
          newEvents[dateKey].push({
            id: w.id,
            title,
            time: timeStr,
            duration,
            color: "bg-primary",
          });
        });

        setEvents(newEvents);
      }
    } catch (err) {
      console.error("Plan optimization failed:", err);
    } finally {
      setIsOptimizing(false);
    }
  };

  return (
    <div className="p-8 h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-semibold text-foreground">Calendar</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Execution Windows & Time Slices
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleOptimizePlan}
            disabled={isOptimizing}
            className="px-4 py-2 bg-primary text-primary-foreground hover:bg-primary/90 text-xs font-semibold rounded-lg transition-colors mr-4 flex items-center gap-1.5 disabled:opacity-50"
          >
            <Sparkles className="w-3.5 h-3.5" />
            {isOptimizing ? "Optimizing..." : "Optimize Focus Plan"}
          </button>
          <button
            onClick={goToPrevWeek}
            className="p-2 rounded-lg hover:bg-muted transition-colors text-muted-foreground"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          <span className="text-sm font-medium text-foreground min-w-[180px] text-center">
            {weekDates[0].toLocaleDateString("en-US", { month: "long", day: "numeric" })}
            {" – "}
            {weekDates[6].toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })}
          </span>
          <button
            onClick={goToNextWeek}
            className="p-2 rounded-lg hover:bg-muted transition-colors text-muted-foreground"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Calendar Grid */}
      <div className="flex-1 bg-card border border-border rounded-xl overflow-hidden flex flex-col">
        {/* Day Headers */}
        <div className="grid grid-cols-[60px_repeat(7,1fr)] border-b border-border">
          <div className="p-3"></div>
          {weekDates.map((date, idx) => {
            const isToday = formatDateKey(date) === "2026-07-07";
            return (
              <div
                key={idx}
                className={`p-3 text-center border-l border-border ${isToday ? "bg-primary/5" : ""}`}
              >
                <p className="text-xs text-muted-foreground">{dayNames[idx]}</p>
                <p
                  className={`text-sm font-semibold mt-0.5 ${
                    isToday ? "text-primary" : "text-foreground"
                  }`}
                >
                  {date.getDate()}
                </p>
              </div>
            );
          })}
        </div>

        {/* Time Grid */}
        <div className="flex-1 overflow-y-auto">
          <div className="grid grid-cols-[60px_repeat(7,1fr)] relative">
            {hours.map((hour) => (
              <div key={hour} className="contents">
                {/* Time Label */}
                <div className="h-16 flex items-start justify-end pr-3 pt-1">
                  <span className="text-xs text-muted-foreground">
                    {hour.toString().padStart(2, "0")}:00
                  </span>
                </div>
                {/* Day Cells */}
                {weekDates.map((date, dayIdx) => {
                  const dateKey = formatDateKey(date);
                  const dayEvents = events[dateKey] || [];
                  const hourEvents = dayEvents.filter(
                    (e) => parseInt(e.time.split(":")[0]) === hour
                  );

                  return (
                    <div
                      key={dayIdx}
                      className="h-16 border-l border-t border-border relative"
                    >
                      {hourEvents.map((event) => (
                        <div
                          key={event.id}
                          className={`absolute left-1 right-1 top-1 rounded-md px-2 py-1 ${event.color}/20 border border-current/10`}
                          style={{
                            height: `${event.duration * 64 - 8}px`,
                          }}
                        >
                          <p className={`text-xs font-medium ${event.color.replace("bg-", "text-")}`}>
                            {event.title}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {event.time} · {event.duration}h
                          </p>
                        </div>
                      ))}
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
