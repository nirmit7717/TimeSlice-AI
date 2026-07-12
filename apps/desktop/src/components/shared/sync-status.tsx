import { useEffect, useState } from "react";
import { Cloud, CloudOff, Check, AlertCircle } from "lucide-react";
import { useOnlineStatus } from "../../hooks/use-online-status";

type SyncState = "synced" | "pending" | "conflict" | "offline";

interface SyncStatusProps {
  lastSynced?: string;
}

export function SyncStatus({ lastSynced: initialLastSynced }: SyncStatusProps) {
  const browserOnline = useOnlineStatus();
  const [status, setStatus] = useState<{
    lastSyncedAt: string | null;
    pendingCount: number;
    conflictCount: number;
    isOnline: boolean;
  }>({
    lastSyncedAt: initialLastSynced || null,
    pendingCount: 0,
    conflictCount: 0,
    isOnline: browserOnline,
  });

  const fetchStatus = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/sync/status");
      if (res.ok) {
        const data = await res.json();
        setStatus({
          lastSyncedAt: data.lastSyncedAt,
          pendingCount: data.pendingCount,
          conflictCount: data.conflictCount,
          isOnline: true,
        });
      } else {
        setStatus((prev) => ({ ...prev, isOnline: false }));
      }
    } catch {
      setStatus((prev) => ({ ...prev, isOnline: false }));
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 8000); // Poll every 8 seconds
    return () => clearInterval(interval);
  }, []);

  const state: SyncState = !status.isOnline
    ? "offline"
    : status.conflictCount > 0
      ? "conflict"
      : status.pendingCount > 0
        ? "pending"
        : "synced";

  const config: Record<SyncState, { icon: typeof Cloud; label: string; color: string }> = {
    synced: { icon: Check, label: "Synced", color: "text-emerald-400" },
    pending: { icon: Cloud, label: `Pending (${status.pendingCount})`, color: "text-muted-foreground" },
    conflict: { icon: AlertCircle, label: `Conflict (${status.conflictCount})`, color: "text-amber-400 font-semibold" },
    offline: { icon: CloudOff, label: "Offline", color: "text-rose-400" },
  };

  const { icon: Icon, label, color } = config[state];

  return (
    <div className={`flex items-center gap-1.5 ${color}`}>
      <Icon className={`w-3.5 h-3.5 ${state === "pending" ? "animate-pulse" : ""}`} />
      <span className="text-xs font-medium">{label}</span>
      {status.lastSyncedAt && state === "synced" && (
        <span className="text-xs text-muted-foreground ml-1">
          {new Date(status.lastSyncedAt).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </span>
      )}
    </div>
  );
}
