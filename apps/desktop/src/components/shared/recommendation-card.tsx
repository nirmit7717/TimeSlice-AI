import { ArrowRight, RotateCcw, HelpCircle } from "lucide-react";

export function RecommendationCard() {
  return (
    <div className="bg-card border border-border rounded-2xl p-8 mb-8">
      {/* Header */}
      <div className="mb-6">
        <p className="text-muted-foreground text-sm mb-2">
          Today&apos;s Recommended Time Slice
        </p>
        <h2 className="text-2xl font-semibold text-foreground">
          Backend Scheduler API
        </h2>
      </div>

      {/* Details Grid */}
      <div className="grid grid-cols-3 gap-8 mb-8 pb-8 border-b border-border">
        <div>
          <p className="text-xs uppercase tracking-wide text-muted-foreground mb-2">
            Duration
          </p>
          <p className="text-lg font-semibold text-foreground">90 Minutes</p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-wide text-muted-foreground mb-2">
            Deadline
          </p>
          <p className="text-lg font-semibold text-foreground">Tomorrow 5 PM</p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-wide text-muted-foreground mb-2">
            Priority
          </p>
          <div className="flex gap-1">
            {[0, 1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className={`w-2 h-6 rounded-sm ${i < 4 ? "bg-primary" : "bg-muted"}`}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Reason */}
      <div className="mb-8">
        <p className="text-xs uppercase tracking-wide text-muted-foreground mb-3">
          Why This?
        </p>
        <ul className="space-y-2">
          <li className="flex gap-3 text-sm text-muted-foreground">
            <span className="text-primary font-bold">•</span>
            <span>Deadline approaching in 22 hours</span>
          </li>
          <li className="flex gap-3 text-sm text-muted-foreground">
            <span className="text-primary font-bold">•</span>
            <span>High Attention Debt accumulated (3.2h)</span>
          </li>
          <li className="flex gap-3 text-sm text-muted-foreground">
            <span className="text-primary font-bold">•</span>
            <span>Best focus window based on your history (8-11 PM)</span>
          </li>
        </ul>
      </div>

      {/* Confidence & Actions */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="w-12 h-12 rounded-lg bg-primary/10 border border-primary/30 flex items-center justify-center">
              <span className="text-primary font-semibold text-sm">92%</span>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Confidence</p>
              <p className="text-sm font-medium text-foreground">Very High</p>
            </div>
          </div>
        </div>

        {/* CTA Buttons */}
        <div className="flex gap-3">
          <button className="px-4 py-2.5 rounded-lg text-sm font-medium text-muted-foreground bg-muted hover:bg-muted/80 transition-colors flex items-center gap-2">
            <HelpCircle className="w-4 h-4" />
            Why This?
          </button>
          <button className="px-4 py-2.5 rounded-lg text-sm font-medium text-muted-foreground bg-muted hover:bg-muted/80 transition-colors flex items-center gap-2">
            <RotateCcw className="w-4 h-4" />
            Reschedule
          </button>
          <button className="px-6 py-2.5 rounded-lg text-sm font-semibold bg-primary text-primary-foreground hover:bg-primary/90 transition-colors flex items-center gap-2">
            Start Time Slice
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
