import { AlertTriangle, ArrowRight, Clock, Zap } from "lucide-react";
import {
  Dialog,
  DialogHeader,
  DialogBody,
  DialogFooter,
} from "../ui/dialog";

interface RescheduleDialogProps {
  open: boolean;
  onClose: () => void;
  onAccept: () => void;
  onReject: () => void;
}

export function RescheduleDialog({
  open,
  onClose,
  onAccept,
  onReject,
}: RescheduleDialogProps) {
  return (
    <Dialog open={open} onClose={onClose}>
      <DialogHeader>
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-lg bg-amber-400/10 flex items-center justify-center">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-foreground">
              Scheduling Conflict
            </h2>
            <p className="text-xs text-muted-foreground">
              The Attention Kernel detected a conflict
            </p>
          </div>
        </div>
      </DialogHeader>

      <DialogBody>
        {/* Conflict description */}
        <div className="bg-muted rounded-xl p-4 mb-4">
          <p className="text-sm text-foreground mb-2 font-medium">
            "Backend Scheduler API" overlaps with a calendar event
          </p>
          <p className="text-xs text-muted-foreground">
            Your 90-minute time slice at 14:00 conflicts with "Team Standup"
            (14:00–14:30). The Kernel suggests rescheduling.
          </p>
        </div>

        {/* Proposed change */}
        <div className="space-y-3 mb-4">
          <p className="text-xs uppercase tracking-wide text-muted-foreground font-medium">
            Proposed Reschedule
          </p>
          <div className="flex items-center gap-4">
            <div className="flex-1 bg-destructive/5 border border-destructive/20 rounded-lg p-3">
              <p className="text-xs text-muted-foreground mb-1">Current</p>
              <p className="text-sm font-medium text-foreground flex items-center gap-1">
                <Clock className="w-3.5 h-3.5 text-destructive" />
                14:00 – 15:30
              </p>
            </div>
            <ArrowRight className="w-4 h-4 text-muted-foreground shrink-0" />
            <div className="flex-1 bg-emerald-400/5 border border-emerald-400/20 rounded-lg p-3">
              <p className="text-xs text-muted-foreground mb-1">Suggested</p>
              <p className="text-sm font-medium text-foreground flex items-center gap-1">
                <Clock className="w-3.5 h-3.5 text-emerald-400" />
                15:00 – 16:30
              </p>
            </div>
          </div>
        </div>

        {/* Impact analysis */}
        <div className="bg-muted rounded-xl p-4">
          <div className="flex items-center gap-2 mb-3">
            <Zap className="w-4 h-4 text-secondary" />
            <p className="text-xs uppercase tracking-wide text-muted-foreground font-medium">
              Cognitive Impact
            </p>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-muted-foreground">Focus disruption</span>
              <span className="text-foreground font-medium">Low</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-muted-foreground">Downstream conflicts</span>
              <span className="text-foreground font-medium">None</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-muted-foreground">Deadline impact</span>
              <span className="text-emerald-400 font-medium">No risk</span>
            </div>
          </div>
        </div>
      </DialogBody>

      <DialogFooter>
        <button
          onClick={onReject}
          className="px-4 py-2.5 rounded-lg text-sm font-medium text-muted-foreground bg-muted hover:bg-muted/80 transition-colors"
        >
          Keep Original
        </button>
        <button
          onClick={onAccept}
          className="px-5 py-2.5 rounded-lg text-sm font-semibold bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
        >
          Accept Reschedule
        </button>
      </DialogFooter>
    </Dialog>
  );
}
