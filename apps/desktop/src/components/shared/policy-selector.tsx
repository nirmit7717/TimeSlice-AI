import { useState } from "react";
import { Check, Shuffle, ArrowUpDown, Timer, CalendarClock } from "lucide-react";
import { cn } from "../../lib/utils";

interface Policy {
  id: string;
  name: string;
  shortName: string;
  icon: typeof Shuffle;
  description: string;
  explanation: string;
  bestFor: string[];
  tradeoffs: string;
}

const policies: Policy[] = [
  {
    id: "round-robin",
    name: "Round Robin",
    shortName: "RR",
    icon: Shuffle,
    description: "Equal attention to all processes in rotation",
    explanation:
      "Each active process receives an equal time slice before rotating to the next. Ensures no process starves but may not optimize for urgency.",
    bestFor: ["Equal priority projects", "Early-stage exploration", "Maintaining breadth"],
    tradeoffs: "Ignores deadlines and priority differences. Best when all processes matter equally.",
  },
  {
    id: "priority",
    name: "Priority Scheduling",
    shortName: "PS",
    icon: ArrowUpDown,
    description: "High-priority processes execute first",
    explanation:
      "Processes are sorted by priority level. Higher priority processes receive time slices before lower ones. Can cause starvation of low-priority work.",
    bestFor: ["Clear priority hierarchy", "Deadline-heavy workloads", "Critical path focus"],
    tradeoffs: "Low-priority processes may accumulate significant Attention Debt if not monitored.",
  },
  {
    id: "sjf",
    name: "Shortest Job First",
    shortName: "SJF",
    icon: Timer,
    description: "Quick-win processes complete first",
    explanation:
      "Processes with the smallest estimated remaining effort execute first. Maximizes completion count but may delay large important projects.",
    bestFor: ["Clearing backlogs", "Momentum building", "Many small tasks"],
    tradeoffs: "Large projects can be perpetually delayed. Works best combined with priority constraints.",
  },
  {
    id: "edf",
    name: "Earliest Deadline First",
    shortName: "EDF",
    icon: CalendarClock,
    description: "Most urgent deadlines get attention first",
    explanation:
      "Processes are sorted by deadline proximity. The process closest to its deadline receives the next time slice. Optimal for preventing missed deadlines.",
    bestFor: ["Deadline-driven work", "Academic schedules", "Client deliverables"],
    tradeoffs: "Long-term projects without hard deadlines may starve. Combine with Attention Debt monitoring.",
  },
];

export function PolicySelector() {
  const [selectedPolicy, setSelectedPolicy] = useState("priority");

  const selected = policies.find((p) => p.id === selectedPolicy)!;

  return (
    <div className="space-y-6">
      {/* Policy Grid */}
      <div className="grid grid-cols-2 gap-3">
        {policies.map((policy) => {
          const isSelected = policy.id === selectedPolicy;
          return (
            <button
              key={policy.id}
              onClick={() => setSelectedPolicy(policy.id)}
              className={cn(
                "relative text-left p-4 rounded-xl border transition-all",
                isSelected
                  ? "bg-primary/5 border-primary/40 ring-1 ring-primary/20"
                  : "bg-card border-border hover:border-primary/20"
              )}
            >
              {isSelected && (
                <div className="absolute top-3 right-3">
                  <Check className="w-4 h-4 text-primary" />
                </div>
              )}
              <div className="flex items-center gap-2 mb-2">
                <div
                  className={cn(
                    "w-8 h-8 rounded-lg flex items-center justify-center",
                    isSelected ? "bg-primary/20" : "bg-muted"
                  )}
                >
                  <policy.icon
                    className={cn(
                      "w-4 h-4",
                      isSelected ? "text-primary" : "text-muted-foreground"
                    )}
                  />
                </div>
                <span
                  className={cn(
                    "text-sm font-semibold",
                    isSelected ? "text-foreground" : "text-foreground"
                  )}
                >
                  {policy.name}
                </span>
              </div>
              <p className="text-xs text-muted-foreground">
                {policy.description}
              </p>
            </button>
          );
        })}
      </div>

      {/* Selected Policy Detail Card */}
      <div className="bg-card border border-border rounded-xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center">
            <selected.icon className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-foreground">
              {selected.name}
            </h3>
            <p className="text-xs text-muted-foreground">Active Policy</p>
          </div>
        </div>

        {/* How it works */}
        <div className="mb-4">
          <p className="text-xs uppercase tracking-wide text-muted-foreground mb-2 font-medium">
            How It Works
          </p>
          <p className="text-sm text-muted-foreground leading-relaxed">
            {selected.explanation}
          </p>
        </div>

        {/* Best For */}
        <div className="mb-4">
          <p className="text-xs uppercase tracking-wide text-muted-foreground mb-2 font-medium">
            Best For
          </p>
          <div className="flex flex-wrap gap-2">
            {selected.bestFor.map((item) => (
              <span
                key={item}
                className="px-2 py-1 rounded-md text-xs font-medium bg-primary/10 text-primary"
              >
                {item}
              </span>
            ))}
          </div>
        </div>

        {/* Tradeoffs */}
        <div className="p-3 bg-amber-400/5 border border-amber-400/20 rounded-lg">
          <p className="text-xs uppercase tracking-wide text-amber-400 mb-1 font-medium">
            Tradeoffs
          </p>
          <p className="text-xs text-muted-foreground">{selected.tradeoffs}</p>
        </div>
      </div>
    </div>
  );
}
