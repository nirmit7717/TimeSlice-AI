const events = [
  { time: "09:00", title: "Backend Scheduler", subtitle: "API Development" },
  { time: "11:00", title: "Azure AZ-900", subtitle: "Certification Study" },
  { time: "15:00", title: "Gym", subtitle: "Exercise" },
  { time: "20:00", title: "Research", subtitle: "New Technologies" },
];

export function Timeline() {
  return (
    <div className="mb-8">
      <h3 className="text-sm font-semibold text-foreground mb-6">
        Today's Timeline
      </h3>
      <div className="space-y-4">
        {events.map((event, idx) => (
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
