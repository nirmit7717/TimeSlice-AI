import { MetricsPanel } from "../components/shared/metrics-panel";
import { PolicySelector } from "../components/shared/policy-selector";

export function AnalyticsPage() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-semibold text-foreground">Analytics</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Process health, scheduling metrics, and policy configuration
        </p>
      </div>

      <div className="grid grid-cols-3 gap-8">
        {/* Metrics — takes 2 columns */}
        <div className="col-span-2">
          <MetricsPanel />
        </div>

        {/* Policy Selector — right column */}
        <div>
          <h3 className="text-sm font-semibold text-foreground mb-4">
            Scheduling Policy
          </h3>
          <PolicySelector />
        </div>
      </div>
    </div>
  );
}
