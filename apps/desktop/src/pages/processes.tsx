import { useState } from "react";
import { Link } from "react-router-dom";
import { Plus, Play, Pause, Clock, AlertTriangle, Archive } from "lucide-react";
import { useProcessStore, type ProcessStatus } from "../stores/process-store";

const statusConfig: Record<
  ProcessStatus,
  { color: string; bg: string }
> = {
  Active: { color: "text-emerald-400", bg: "bg-emerald-400/10" },
  Paused: { color: "text-amber-400", bg: "bg-amber-400/10" },
  Completed: { color: "text-blue-400", bg: "bg-blue-400/10" },
  Archived: { color: "text-slate-400", bg: "bg-slate-400/10" },
};

type FilterTab = "All" | ProcessStatus;

export function ProcessesPage() {
  const { processes, pauseProcess, resumeProcess, archiveProcess } = useProcessStore();
  const [activeTab, setActiveTab] = useState<FilterTab>("All");

  const filteredProcesses =
    activeTab === "All"
      ? processes
      : processes.filter((p) => p.status === activeTab);

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-semibold text-foreground">Processes</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Manage your active projects and their lifecycle
          </p>
        </div>
        <Link
          to="/processes/new"
          className="px-4 py-2.5 rounded-lg text-sm font-semibold bg-primary text-primary-foreground hover:bg-primary/90 transition-colors flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          New Process
        </Link>
      </div>

      {/* Status Filter Tabs */}
      <div className="flex gap-2 mb-6">
        {(["All", "Active", "Paused", "Completed", "Archived"] as FilterTab[]).map(
          (tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                tab === activeTab
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:text-foreground hover:bg-muted"
              }`}
            >
              {tab}
              {tab !== "All" && (
                <span className="ml-1.5 text-muted-foreground">
                  {processes.filter((p) => p.status === tab).length}
                </span>
              )}
            </button>
          )
        )}
      </div>

      {/* Process List */}
      <div className="space-y-3">
        {filteredProcesses.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground text-sm">
              No processes found for this filter.
            </p>
          </div>
        ) : (
          filteredProcesses.map((process) => {
            const config = statusConfig[process.status];
            return (
              <div
                key={process.id}
                className="bg-card border border-border rounded-xl p-5 hover:border-primary/30 transition-colors"
              >
                <div className="flex items-start gap-6">
                  {/* Left: Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-sm font-semibold text-foreground truncate">
                        {process.name}
                      </h3>
                      <div
                        className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-xs font-medium ${config.bg} ${config.color}`}
                      >
                        <span className="w-1.5 h-1.5 rounded-full bg-current"></span>
                        {process.status}
                      </div>
                    </div>
                    <p className="text-xs text-muted-foreground mb-3">
                      {process.description}
                    </p>

                    {/* Progress */}
                    <div className="flex items-center gap-4">
                      <div className="flex-1 max-w-xs">
                        <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                          <div
                            className="h-full bg-primary transition-all"
                            style={{ width: `${process.progress}%` }}
                          />
                        </div>
                      </div>
                      <span className="text-xs text-muted-foreground">
                        {process.progress}%
                      </span>
                    </div>
                  </div>

                  {/* Right: Metrics + Actions */}
                  <div className="flex items-center gap-6 text-xs shrink-0">
                    <div className="text-center">
                      <p className="text-muted-foreground mb-1">Priority</p>
                      <div className="flex gap-0.5">
                        {[0, 1, 2, 3, 4].map((i) => (
                          <div
                            key={i}
                            className={`w-1.5 h-4 rounded-sm ${
                              i < process.priority ? "bg-primary" : "bg-muted"
                            }`}
                          />
                        ))}
                      </div>
                    </div>
                    <div className="text-center">
                      <p className="text-muted-foreground mb-1">Attn Debt</p>
                      <p className="font-semibold text-foreground flex items-center gap-1">
                        {process.attentionDebt > 5 && (
                          <AlertTriangle className="w-3 h-3 text-amber-400" />
                        )}
                        {process.attentionDebt}h
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-muted-foreground mb-1">Effort</p>
                      <p className="font-semibold text-foreground flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {process.estimatedEffort}h
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-muted-foreground mb-1">Deadline</p>
                      <p className="font-semibold text-foreground">
                        {new Date(process.deadline).toLocaleDateString("en-US", {
                          month: "short",
                          day: "numeric",
                        })}
                      </p>
                    </div>

                    {/* Action buttons */}
                    <div className="flex gap-1">
                      {process.status === "Active" && (
                        <button
                          onClick={() => pauseProcess(process.id)}
                          className="p-1.5 rounded-lg hover:bg-muted transition-colors text-muted-foreground hover:text-amber-400"
                          title="Pause"
                        >
                          <Pause className="w-4 h-4" />
                        </button>
                      )}
                      {process.status === "Paused" && (
                        <button
                          onClick={() => resumeProcess(process.id)}
                          className="p-1.5 rounded-lg hover:bg-muted transition-colors text-muted-foreground hover:text-emerald-400"
                          title="Resume"
                        >
                          <Play className="w-4 h-4" />
                        </button>
                      )}
                      {process.status !== "Archived" && (
                        <button
                          onClick={() => archiveProcess(process.id)}
                          className="p-1.5 rounded-lg hover:bg-muted transition-colors text-muted-foreground hover:text-slate-400"
                          title="Archive"
                        >
                          <Archive className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
