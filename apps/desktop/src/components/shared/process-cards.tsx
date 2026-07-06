import { Play, Pause, Clock } from "lucide-react";

const processes = [
  {
    name: "Backend Scheduler API",
    status: "Running",
    progress: 65,
    attentionDebt: "3.2h",
    deadline: "Tomorrow 5 PM",
    remaining: "2h 15m",
    statusColor: "text-emerald-400",
    statusBg: "bg-emerald-400/10",
  },
  {
    name: "Azure Certification Study",
    status: "Ready",
    progress: 28,
    attentionDebt: "5.1h",
    deadline: "In 3 days",
    remaining: "12h 40m",
    statusColor: "text-blue-400",
    statusBg: "bg-blue-400/10",
  },
  {
    name: "Q4 Planning Review",
    status: "Waiting",
    progress: 12,
    attentionDebt: "8.5h",
    deadline: "In 1 week",
    remaining: "24h 30m",
    statusColor: "text-amber-400",
    statusBg: "bg-amber-400/10",
  },
  {
    name: "Code Review Session",
    status: "Paused",
    progress: 45,
    attentionDebt: "1.5h",
    deadline: "In 2 days",
    remaining: "1h 20m",
    statusColor: "text-slate-400",
    statusBg: "bg-slate-400/10",
  },
];

export function ProcessCards() {
  return (
    <div>
      <h3 className="text-sm font-semibold text-foreground mb-6">
        Running Processes
      </h3>
      <div className="grid grid-cols-2 gap-4">
        {processes.map((process, idx) => (
          <div
            key={idx}
            className="bg-card border border-border rounded-xl p-5 hover:border-primary/30 transition-colors"
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h4 className="text-sm font-semibold text-foreground mb-1">
                  {process.name}
                </h4>
                <div
                  className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-medium ${process.statusBg} ${process.statusColor}`}
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-current"></span>
                  {process.status}
                </div>
              </div>
              <button className="p-1.5 rounded-lg hover:bg-muted transition-colors text-muted-foreground">
                {process.status === "Running" ? (
                  <Pause className="w-4 h-4" />
                ) : (
                  <Play className="w-4 h-4" />
                )}
              </button>
            </div>

            {/* Progress Bar */}
            <div className="mb-4">
              <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary transition-all"
                  style={{ width: `${process.progress}%` }}
                />
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                {process.progress}% Complete
              </p>
            </div>

            {/* Metrics */}
            <div className="space-y-2 mb-4 pb-4 border-t border-border pt-4">
              <div className="flex justify-between items-center text-xs">
                <span className="text-muted-foreground">Attention Debt</span>
                <span className="font-semibold text-foreground">
                  {process.attentionDebt}
                </span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="text-muted-foreground flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  Est. Remaining
                </span>
                <span className="font-semibold text-foreground">
                  {process.remaining}
                </span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="text-muted-foreground">Deadline</span>
                <span className="font-semibold text-foreground">
                  {process.deadline}
                </span>
              </div>
            </div>

            {/* Footer Action */}
            <button className="w-full px-3 py-2 rounded-lg text-xs font-medium text-muted-foreground bg-muted hover:bg-muted/80 transition-colors">
              View Details
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
