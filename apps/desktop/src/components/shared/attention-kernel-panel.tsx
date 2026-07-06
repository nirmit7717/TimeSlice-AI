import { Brain, Zap } from "lucide-react";

export function AttentionKernelPanel() {
  return (
    <aside className="w-80 bg-card border-l border-border h-full flex flex-col p-6 overflow-y-auto">
      {/* Header */}
      <div className="flex items-center gap-2 mb-8">
        <div className="w-8 h-8 rounded-lg bg-secondary/20 border border-secondary/30 flex items-center justify-center">
          <Brain className="w-4 h-4 text-secondary" />
        </div>
        <h2 className="text-sm font-semibold text-foreground">
          Attention Kernel
        </h2>
      </div>

      {/* Recommendation Card 1 */}
      <div className="bg-muted border border-border rounded-xl p-4 mb-6">
        <p className="text-xs uppercase tracking-wide text-muted-foreground mb-3">
          Recommendation
        </p>
        <h3 className="text-sm font-semibold text-foreground mb-4">
          Continue Backend Scheduler
        </h3>

        <div className="mb-4 p-3 bg-background rounded-lg border border-border">
          <p className="text-xs text-muted-foreground leading-relaxed">
            Your completion rate increases by{" "}
            <span className="text-primary font-semibold">18%</span> during
            evening coding sessions. Starting now will optimize your focus
            window.
          </p>
        </div>

        {/* Confidence Badge */}
        <div className="flex items-center gap-2 mb-4 pb-4 border-b border-border">
          <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center">
            <span className="text-xs font-bold text-primary">92%</span>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Confidence</p>
            <p className="text-xs font-medium text-foreground">Very High</p>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="space-y-2">
          <button className="w-full px-3 py-2 rounded-lg text-xs font-medium text-muted-foreground bg-background hover:bg-background/80 transition-colors border border-border">
            Explain
          </button>
          <button className="w-full px-3 py-2 rounded-lg text-xs font-medium text-muted-foreground bg-background hover:bg-background/80 transition-colors border border-border">
            Adjust Schedule
          </button>
          <button className="w-full px-3 py-2 rounded-lg text-xs font-medium text-muted-foreground bg-background hover:bg-background/80 transition-colors border border-border">
            Generate Checklist
          </button>
        </div>
      </div>

      {/* Recommendation Card 2 */}
      <div className="bg-muted border border-border rounded-xl p-4 mb-6">
        <p className="text-xs uppercase tracking-wide text-muted-foreground mb-3">
          AI Insight
        </p>
        <h3 className="text-sm font-semibold text-foreground mb-4">
          Optimal Break Time
        </h3>

        <div className="mb-4 p-3 bg-background rounded-lg border border-border">
          <p className="text-xs text-muted-foreground leading-relaxed">
            After 90 minutes of focus, take a{" "}
            <span className="text-primary font-semibold">15-min break</span>.
            This matches your peak performance pattern.
          </p>
        </div>

        {/* Confidence Badge */}
        <div className="flex items-center gap-2 mb-4 pb-4 border-b border-border">
          <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center">
            <span className="text-xs font-bold text-primary">87%</span>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Confidence</p>
            <p className="text-xs font-medium text-foreground">High</p>
          </div>
        </div>

        <button className="w-full px-3 py-2 rounded-lg text-xs font-medium text-muted-foreground bg-background hover:bg-background/80 transition-colors border border-border">
          Dismiss
        </button>
      </div>

      {/* Status Summary */}
      <div className="mt-auto pt-6 border-t border-border">
        <div className="space-y-4">
          <div>
            <p className="text-xs text-muted-foreground mb-2">Attention Debt</p>
            <div className="flex items-center justify-between">
              <div className="text-sm font-semibold text-foreground">
                17.8 hours
              </div>
              <span className="text-xs px-2 py-1 rounded-md bg-amber-400/10 text-amber-400 font-medium">
                High
              </span>
            </div>
          </div>

          <div>
            <p className="text-xs text-muted-foreground mb-2">
              Today's Focus
            </p>
            <div className="flex items-center justify-between">
              <div className="text-sm font-semibold text-foreground">
                3h 45m
              </div>
              <span className="text-xs px-2 py-1 rounded-md bg-emerald-400/10 text-emerald-400 font-medium">
                On Track
              </span>
            </div>
          </div>

          <div>
            <p className="text-xs text-muted-foreground mb-2">Focus Streak</p>
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-foreground">
                12 days
              </span>
              <Zap className="w-4 h-4 text-primary" />
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
