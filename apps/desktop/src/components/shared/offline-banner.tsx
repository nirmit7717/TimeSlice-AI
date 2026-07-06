import { WifiOff, Database } from "lucide-react";
import { useOnlineStatus } from "../../hooks/use-online-status";

export function OfflineBanner() {
  const isOnline = useOnlineStatus();

  if (isOnline) return null;

  return (
    <div className="bg-amber-400/10 border-b border-amber-400/20 px-4 py-2 flex items-center justify-center gap-3">
      <WifiOff className="w-4 h-4 text-amber-400" />
      <p className="text-xs font-medium text-amber-400">
        You're offline — changes are saved locally
      </p>
      <div className="flex items-center gap-1 text-xs text-muted-foreground">
        <Database className="w-3 h-3" />
        <span>Local cache active</span>
      </div>
    </div>
  );
}
