import { useState } from "react";
import { AlertCircle, Monitor, Cloud, Check } from "lucide-react";

interface ConflictItem {
  id: string;
  processName: string;
  field: string;
  localValue: string;
  cloudValue: string;
  timestamp: { local: string; cloud: string };
}

const mockConflicts: ConflictItem[] = [
  {
    id: "conflict-1",
    processName: "Backend Scheduler API",
    field: "Progress",
    localValue: "68%",
    cloudValue: "65%",
    timestamp: { local: "Jul 7, 00:15", cloud: "Jul 6, 23:45" },
  },
  {
    id: "conflict-2",
    processName: "Azure AZ-900 Certification",
    field: "Status",
    localValue: "Active",
    cloudValue: "Paused",
    timestamp: { local: "Jul 7, 00:10", cloud: "Jul 6, 22:30" },
  },
  {
    id: "conflict-3",
    processName: "Q4 Planning Review",
    field: "Priority",
    localValue: "4 (High)",
    cloudValue: "3 (Medium)",
    timestamp: { local: "Jul 6, 23:50", cloud: "Jul 6, 21:00" },
  },
];

type Resolution = "local" | "cloud";

export function SyncConflictPanel() {
  const [resolutions, setResolutions] = useState<Record<string, Resolution>>(
    {}
  );
  const [resolved, setResolved] = useState<string[]>([]);

  const setResolution = (id: string, choice: Resolution) => {
    setResolutions((prev) => ({ ...prev, [id]: choice }));
  };

  const applyResolutions = () => {
    const resolvedIds = Object.keys(resolutions);
    setResolved((prev) => [...prev, ...resolvedIds]);
    setResolutions({});
  };

  const unresolvedConflicts = mockConflicts.filter(
    (c) => !resolved.includes(c.id)
  );

  if (unresolvedConflicts.length === 0) {
    return (
      <div className="bg-card border border-border rounded-xl p-8 text-center">
        <div className="w-12 h-12 rounded-full bg-emerald-400/10 flex items-center justify-center mx-auto mb-4">
          <Check className="w-6 h-6 text-emerald-400" />
        </div>
        <h3 className="text-sm font-semibold text-foreground mb-1">
          All Synced
        </h3>
        <p className="text-xs text-muted-foreground">
          No conflicts to resolve. Local and cloud are in sync.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-3 mb-2">
        <div className="w-8 h-8 rounded-lg bg-amber-400/10 flex items-center justify-center">
          <AlertCircle className="w-4 h-4 text-amber-400" />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-foreground">
            Sync Conflicts ({unresolvedConflicts.length})
          </h3>
          <p className="text-xs text-muted-foreground">
            Choose which version to keep for each conflict
          </p>
        </div>
      </div>

      {/* Conflict Cards */}
      <div className="space-y-3">
        {unresolvedConflicts.map((conflict) => {
          const choice = resolutions[conflict.id];
          return (
            <div
              key={conflict.id}
              className="bg-card border border-border rounded-xl p-4"
            >
              <div className="flex items-center justify-between mb-3">
                <div>
                  <p className="text-sm font-medium text-foreground">
                    {conflict.processName}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Field: {conflict.field}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                {/* Local version */}
                <button
                  onClick={() => setResolution(conflict.id, "local")}
                  className={`p-3 rounded-lg border text-left transition-all ${
                    choice === "local"
                      ? "border-primary bg-primary/5 ring-1 ring-primary/20"
                      : "border-border hover:border-primary/20"
                  }`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <Monitor className="w-3.5 h-3.5 text-primary" />
                    <span className="text-xs font-medium text-muted-foreground">
                      Local
                    </span>
                    {choice === "local" && (
                      <Check className="w-3 h-3 text-primary ml-auto" />
                    )}
                  </div>
                  <p className="text-sm font-semibold text-foreground">
                    {conflict.localValue}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {conflict.timestamp.local}
                  </p>
                </button>

                {/* Cloud version */}
                <button
                  onClick={() => setResolution(conflict.id, "cloud")}
                  className={`p-3 rounded-lg border text-left transition-all ${
                    choice === "cloud"
                      ? "border-secondary bg-secondary/5 ring-1 ring-secondary/20"
                      : "border-border hover:border-secondary/20"
                  }`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <Cloud className="w-3.5 h-3.5 text-secondary" />
                    <span className="text-xs font-medium text-muted-foreground">
                      Cloud
                    </span>
                    {choice === "cloud" && (
                      <Check className="w-3 h-3 text-secondary ml-auto" />
                    )}
                  </div>
                  <p className="text-sm font-semibold text-foreground">
                    {conflict.cloudValue}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {conflict.timestamp.cloud}
                  </p>
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Apply button */}
      {Object.keys(resolutions).length > 0 && (
        <button
          onClick={applyResolutions}
          className="w-full px-4 py-2.5 rounded-lg text-sm font-semibold bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
        >
          Apply Resolutions ({Object.keys(resolutions).length}/
          {unresolvedConflicts.length})
        </button>
      )}
    </div>
  );
}
