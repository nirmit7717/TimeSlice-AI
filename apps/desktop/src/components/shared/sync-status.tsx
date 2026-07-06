import { Cloud, CloudOff, Check } from "lucide-react";
import { useOnlineStatus } from "../../hooks/use-online-status";

type SyncState = "synced" | "pending" | "offline";

interface SyncStatusProps {
  lastSynced?: string;
}

export function SyncStatus({ lastSynced }: SyncStatusProps) {
  const isOnline = useOnlineStatus();

  const state: SyncState = !isOnline
    ? "offline"
    : !lastSynced
      ? "pending"
      : "synced";

  const config: Record<SyncState, { icon: typeof Cloud; label: string; color: string }> = {
    synced: { icon: Check, label: "Synced", color: "text-emerald-400" },
    pending: { icon: Cloud, label: "Pending", color: "text-muted-foreground" },
    offline: { icon: CloudOff, label: "Offline", color: "text-amber-400" },
  };

  const { icon: Icon, label, color } = config[state];

  return (
    <div className={`flex items-center gap-1.5 ${color}`}>
      <Icon className={`w-3.5 h-3.5 ${state === "pending" ? "animate-pulse" : ""}`} />
      <span className="text-xs font-medium">{label}</span>
      {lastSynced && state === "synced" && (
        <span className="text-xs text-muted-foreground ml-1">
          {new Date(lastSynced).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </span>
      )}
    </div>
  );
}
