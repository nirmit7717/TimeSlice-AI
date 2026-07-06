import { RecommendationCard } from "../components/shared/recommendation-card";
import { Timeline } from "../components/shared/timeline";
import { ProcessCards } from "../components/shared/process-cards";
import { Insights } from "../components/shared/insights";

export function DashboardPage() {
  return (
    <div className="p-8">
      {/* Greeting */}
      <div className="mb-8">
        <h1 className="text-3xl font-semibold text-foreground">Good Evening</h1>
      </div>

      {/* Hero Recommendation */}
      <RecommendationCard />

      {/* Timeline and Processes Grid */}
      <div className="grid grid-cols-3 gap-8 mb-8">
        <div className="col-span-1">
          <Timeline />
        </div>
        <div className="col-span-2">
          <ProcessCards />
        </div>
      </div>

      {/* Insights */}
      <Insights />
    </div>
  );
}
