import { ChevronLeft, ChevronRight, Sparkles } from "lucide-react";
import { useState } from "react";
import { usePreferencesStore } from "../stores/preferences-store";

// Calendar system page loaded dynamically from backend store
import { useCalendarStore } from "../stores/calendar-store";

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

import { useEffect } from "react";

export function CalendarPage() {
  const activePolicy = usePreferencesStore((s) => s.activePolicy);
  const maxDailyFocusHours = usePreferencesStore((s) => s.maxDailyFocusHours);
  const calendarStore = useCalendarStore();

  const [currentDate, setCurrentDate] = useState(new Date("2026-07-07"));
  const [isOptimizing, setIsOptimizing] = useState(false);

  const weekDates = getWeekDates(currentDate);

  // Fetch events from backend when the week changes
  useEffect(() => {
    const startStr = weekDates[0].toISOString();
    const endStr = weekDates[6].toISOString();
    calendarStore.fetchEvents(startStr, endStr);
  }, [currentDate]);

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
        // After optimization, reload the events list which pulls in the new execution windows
        const startStr = weekDates[0].toISOString();
        const endStr = weekDates[6].toISOString();
        await calendarStore.fetchEvents(startStr, endStr);
      }
    } catch (err) {
      console.error("Plan optimization failed:", err);
    } finally {
      setIsOptimizing(false);
    }
  };

  const handleSyncGoogle = async () => {
    await calendarStore.syncGoogleCalendar();
    // Re-fetch calendar events after sync attempt
    const startStr = weekDates[0].toISOString();
    const endStr = weekDates[6].toISOString();
    await calendarStore.fetchEvents(startStr, endStr);
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
            onClick={handleSyncGoogle}
            className="px-4 py-2 border border-border hover:bg-muted text-foreground text-xs font-semibold rounded-lg transition-colors mr-1 flex items-center gap-1.5"
          >
            Sync Google Calendar
          </button>
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
                  // Find events matching this date and hour
                  const dayEvents = calendarStore.events.filter((e) => {
                    const eventDate = e.start_time.split("T")[0];
                    return eventDate === dateKey;
                  });
                  const hourEvents = dayEvents.filter((e) => {
                    const eventHour = new Date(e.start_time).getHours();
                    return eventHour === hour;
                  });

                  return (
                    <div
                      key={dayIdx}
                      className="h-16 border-l border-t border-border relative"
                    >
                      {hourEvents.map((event) => {
                        // Calculate duration in hours
                        const start = new Date(event.start_time);
                        const end = new Date(event.end_time);
                        const durationHours = (end.getTime() - start.getTime()) / (1000 * 60 * 60);
                        const timeStr = start.toTimeString().substring(0, 5);

                        let colorClass = "bg-primary text-primary";
                        if (event.source === "google") colorClass = "bg-emerald-500 text-emerald-500";
                        if (event.is_rest_period) colorClass = "bg-muted text-muted-foreground";

                        return (
                          <div
                            key={event.id}
                            className={`absolute left-1 right-1 top-1 rounded-md px-2 py-1 ${colorClass.split(" ")[0]}/20 border border-current/10 z-10`}
                            style={{
                              height: `${durationHours * 64 - 8}px`,
                            }}
                          >
                            <p className={`text-xs font-semibold ${colorClass.split(" ")[1]}`}>
                              {event.title}
                            </p>
                            <p className="text-[10px] text-muted-foreground">
                              {timeStr} · {durationHours.toFixed(1)}h
                            </p>
                          </div>
                        );
                      })}
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
