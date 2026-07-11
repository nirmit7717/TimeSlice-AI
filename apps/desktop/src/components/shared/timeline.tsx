import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/services/api-client";

interface TimelineEntry {
  time: string;
  title: string;
  subtitle: string;
  processId?: string;
}

function mapPlanToTimeline(plan: any): TimelineEntry[] {
  if (!plan?.executionWindows?.length) return [];
  return plan.executionWindows
    .filter((w: any) => {
      const start = new Date(w.timeSlice?.startTime ?? w.timeSlice?.start_time);
      const today = new Date();
      return (
        start.getFullYear() === today.getFullYear() &&
        start.getMonth() === today.getMonth() &&
        start.getDate() === today.getDate()
      );
    })
    .map((w: any) => {
      const ts = w.timeSlice ?? w.time_slice;
      const start = new Date(ts.startTime ?? ts.start_time);
      return {
        time: start.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        title: ts.processId ?? ts.process_id ?? "Process",
        subtitle: `${ts.durationHours ?? ts.duration_hours ?? 0}h session`,
        processId: ts.processId ?? ts.process_id,
      };
    });
}

export function Timeline() {
  const { data: plan, isLoading } = useQuery({
    queryKey: ["execution-plan-today"],
    queryFn: async () => {
      try {
        const response = await apiClient.get("/scheduler/plan", {
          params: {
            policy_name: "round_robin",
            quantum_hours: 2,
            available_hours: 8,
          },
        });
        return response.data;
      } catch {
        return null;
      }
    },
    staleTime: 5 * 60 * 1000,
  });

  const events = plan ? mapPlanToTimeline(plan) : [];

  return (
    <div className="mb-8">
      <h3 className="text-sm font-semibold text-foreground mb-6">
        Today's Timeline
      </h3>
      <div className="space-y-4">
        {isLoading && (
          <div className="space-y-4">
            {[0, 1, 2].map((i) => (
              <div key={i} className="flex gap-6 items-start animate-pulse">
                <div className="h-4 w-16 bg-muted rounded" />
                <div className="w-3 h-3 rounded-full bg-muted mt-1" />
                <div className="flex-1">
                  <div className="h-3 w-32 bg-muted rounded mb-2" />
                  <div className="h-2 w-20 bg-muted rounded" />
                </div>
              </div>
            ))}
          </div>
        )}

        {!isLoading && events.length === 0 && (
          <div className="py-6 text-center">
            <p className="text-sm text-muted-foreground">
              No sessions scheduled for today.
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Generate an execution plan from the calendar to see your timeline.
            </p>
          </div>
        )}

        {!isLoading &&
          events.map((event, idx) => (
            <div key={idx} className="flex gap-6 items-start">
              {/* Time */}
              <div className="pt-1">
                <p className="text-sm font-medium text-primary w-16">
                  {event.time}
                </p>
              </div>

              {/* Connector Line */}
              <div className="flex flex-col items-center">
                <div className="w-3 h-3 rounded-full bg-primary border-2 border-card" />
                {idx < events.length - 1 && (
                  <div className="w-0.5 h-12 bg-border mt-2" />
                )}
              </div>

              {/* Event */}
              <div className="flex-1 pt-1">
                <p className="text-sm font-medium text-foreground">
                  {event.title}
                </p>
                <p className="text-xs text-muted-foreground">{event.subtitle}</p>
              </div>
            </div>
          ))}
      </div>
    </div>
  );
}
