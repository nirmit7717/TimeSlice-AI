import { useEffect, useState } from "react";
import { AlertCircle, Monitor, Cloud, Check } from "lucide-react";

interface ConflictItem {
  id: string;
  recordId: string;
  tableName: string;
  field: string;
  localValue: string;
  cloudValue: string;
  localUpdatedAt: string;
  cloudUpdatedAt: string;
  processName: string;
}

type Resolution = "local" | "cloud";

export function SyncConflictPanel() {
  const [conflicts, setConflicts] = useState<ConflictItem[]>([]);
  const [resolutions, setResolutions] = useState<Record<string, Resolution>>({});
  const [isLoading, setIsLoading] = useState(true);

  const fetchConflicts = async () => {
    setIsLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/v1/sync/conflicts");
      if (res.ok) {
        const data = await res.json();
        setConflicts(data);
      }
    } catch (err) {
      console.error("Failed to load sync conflicts:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchConflicts();
  }, []);

  const setResolution = (id: string, choice: Resolution) => {
    setResolutions((prev) => ({ ...prev, [id]: choice }));
  };

  const applyResolutions = async () => {
    for (const [id, choice] of Object.entries(resolutions)) {
      const conflict = conflicts.find((c) => c.id === id);
      if (!conflict) continue;

      // Construct cloud payload if resolving using cloud values
      const cloudPayload = choice === "cloud"
        ? conflict.tableName === "processes"
          ? { name: conflict.cloudValue }
          : { status: conflict.cloudValue }
        : null;

      try {
        const res = await fetch(`http://localhost:8000/api/v1/sync/conflicts/${encodeURIComponent(id)}/resolve`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            resolution: choice,
            cloudPayload,
          }),
        });
        if (!res.ok) {
          console.error(`Failed to resolve conflict ${id}`);
        }
      } catch (err) {
        console.error("Network error during resolution:", err);
      }
    }

    setResolutions({});
    fetchConflicts();
  };

  if (isLoading) {
    return (
      <div className="bg-card border border-border rounded-xl p-8 text-center">
        <p className="text-xs text-muted-foreground animate-pulse">
          Querying cloud conflicts database...
        </p>
      </div>
    );
  }

  if (conflicts.length === 0) {
    return (
      <div className="bg-card border border-border rounded-xl p-8 text-center">
        <div className="w-12 h-12 rounded-full bg-emerald-400/10 flex items-center justify-center mx-auto mb-4">
          <Check className="w-6 h-6 text-emerald-400" />
        </div>
        <h3 className="text-sm font-semibold text-foreground mb-1">
          All Synced
        </h3>
        <p className="text-xs text-muted-foreground">
          No conflicts to resolve. Local and cloud databases are perfectly aligned.
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
            Sync Conflicts ({conflicts.length})
          </h3>
          <p className="text-xs text-muted-foreground">
            Choose which version to keep for each conflict
          </p>
        </div>
      </div>

      {/* Conflict Cards */}
      <div className="space-y-3">
        {conflicts.map((conflict) => {
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
                      <Check className="w-3.5 h-3.5 text-primary ml-auto" />
                    )}
                  </div>
                  <p className="text-sm font-semibold text-foreground break-all">
                    {conflict.localValue}
                  </p>
                  <p className="text-[10px] text-muted-foreground mt-1">
                    {new Date(conflict.localUpdatedAt).toLocaleDateString([], {
                      month: "short",
                      day: "numeric",
                      hour: "2-digit",
                      minute: "2-digit"
                    })}
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
                      <Check className="w-3.5 h-3.5 text-secondary ml-auto" />
                    )}
                  </div>
                  <p className="text-sm font-semibold text-foreground break-all">
                    {conflict.cloudValue}
                  </p>
                  <p className="text-[10px] text-muted-foreground mt-1">
                    {new Date(conflict.cloudUpdatedAt).toLocaleDateString([], {
                      month: "short",
                      day: "numeric",
                      hour: "2-digit",
                      minute: "2-digit"
                    })}
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
          className="w-full px-4 py-2.5 rounded-lg text-sm font-semibold bg-primary text-primary-foreground hover:bg-primary/90 transition-colors cursor-pointer"
        >
          Apply Resolutions ({Object.keys(resolutions).length}/
          {conflicts.length})
        </button>
      )}
    </div>
  );
}
