import { Play, Pause, Clock } from "lucide-react";
import { useProcessStore } from "../../stores/process-store";

export function ProcessCards() {
  const { processes, pauseProcess, resumeProcess } = useProcessStore();
  
  // Display first 4 processes on dashboard
  const running = processes.slice(0, 4);

  return (
    <div>
      <h3 className="text-sm font-semibold text-foreground mb-6">
        Running Processes
      </h3>
      {running.length === 0 ? (
        <div className="bg-card border border-border rounded-xl p-8 text-center text-sm text-muted-foreground">
          No active processes found. Create a process to get started.
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4">
          {running.map((process) => {
            const isRunning = process.status === "Active";
            return (
              <div
                key={process.id}
                className="bg-card border border-border rounded-xl p-5 hover:border-primary/30 transition-colors"
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-semibold text-foreground mb-1 truncate">
                      {process.name}
                    </h4>
                    <div
                      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[10px] font-medium ${
                        isRunning
                          ? "bg-emerald-400/10 text-emerald-400"
                          : "bg-slate-400/10 text-slate-400"
                      }`}
                    >
                      <span className="w-1.5 h-1.5 rounded-full bg-current"></span>
                      {process.status}
                    </div>
                  </div>
                  <button
                    onClick={() => isRunning ? pauseProcess(process.id) : resumeProcess(process.id)}
                    className="p-1.5 rounded-lg hover:bg-muted transition-colors text-muted-foreground shrink-0 ml-2"
                  >
                    {isRunning ? (
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
                  <p className="text-[11px] text-muted-foreground mt-2">
                    {process.progress}% Complete
                  </p>
                </div>

                {/* Metrics */}
                <div className="space-y-2 mb-4 pb-4 border-t border-border pt-4">
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-muted-foreground">Attention Debt</span>
                    <span className="font-semibold text-foreground">
                      {process.attentionDebt.toFixed(1)}h
                    </span>
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-muted-foreground flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      Est. Remaining
                    </span>
                    <span className="font-semibold text-foreground">
                      {Math.max(0, process.estimatedEffort - Math.round(process.estimatedEffort * (process.progress / 100)))}h
                    </span>
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-muted-foreground">Deadline</span>
                    <span className="font-semibold text-foreground truncate max-w-[120px]">
                      {process.deadline}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
