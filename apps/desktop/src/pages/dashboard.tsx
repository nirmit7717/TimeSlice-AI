import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { RecommendationCard } from "../components/shared/recommendation-card";
import { Timeline } from "../components/shared/timeline";
import { ProcessCards } from "../components/shared/process-cards";
import { Insights } from "../components/shared/insights";
import { Onboarding } from "../components/shared/onboarding";
import { useProcessStore } from "../stores/process-store";

function getGreeting() {
  const h = new Date().getHours();
  if (h < 12) return "Good Morning";
  if (h < 17) return "Good Afternoon";
  return "Good Evening";
}

export function DashboardPage() {
  const [triggerCrash, setTriggerCrash] = useState(false);
  const processes = useProcessStore((s) => s.processes);
  const navigate = useNavigate();

  if (triggerCrash) {
    throw new Error("Simulated telemetry crash exception: Render call stack corrupted.");
  }

  // Show onboarding flow for new users with no processes
  if (processes.length === 0) {
    return (
      <div className="p-8">
        <Onboarding onCreateProcess={() => navigate("/processes/new")} />
      </div>
    );
  }

  return (
    <div className="p-8">
      {/* Greeting */}
      <div className="mb-8 flex items-center justify-between">
        <h1 className="text-3xl font-semibold text-foreground">{getGreeting()}</h1>
        <button
          onClick={() => setTriggerCrash(true)}
          className="px-3 py-1.5 bg-destructive/10 hover:bg-destructive/20 border border-destructive/20 rounded-lg text-[11px] font-bold text-destructive transition-colors shadow-sm"
        >
          Trigger Crash Test
        </button>
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

