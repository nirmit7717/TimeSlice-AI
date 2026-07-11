import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowRight, RotateCcw, HelpCircle, Loader2, Zap } from "lucide-react";
import { apiClient } from "@/services/api-client";

interface Recommendation {
  process_name: string;
  process_id: string;
  policy_name: string;
  duration_hours: number;
  deadline: string | null;
  priority: number;
  attention_debt: number;
  confidence_score: number;
  reasons: string[];
}

function PriorityDots({ level }: { level: number }) {
  return (
    <div className="flex gap-1">
      {[0, 1, 2, 3, 4].map((i) => (
        <div
          key={i}
          className={`w-2 h-6 rounded-sm ${i < level ? "bg-primary" : "bg-muted"}`}
        />
      ))}
    </div>
  );
}

export function RecommendationCard() {
  const queryClient = useQueryClient();

  const { data: rec, isLoading, isError } = useQuery<Recommendation>({
    queryKey: ["scheduler-recommendation"],
    queryFn: async () => {
      const res = await apiClient.get("/scheduler/recommendation");
      return res.data;
    },
    staleTime: 3 * 60 * 1000,
    retry: false,
  });

  const recomputeMutation = useMutation({
    mutationFn: async () => {
      await apiClient.post("/scheduler/recompute");
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scheduler-recommendation"] });
      queryClient.invalidateQueries({ queryKey: ["execution-plan-today"] });
    },
  });

  // ── Loading State ──────────────────────────────────────────────────────────
  if (isLoading) {
    return (
      <div className="bg-card border border-border rounded-2xl p-8 mb-8 animate-pulse">
        <div className="h-3 w-40 bg-muted rounded mb-3" />
        <div className="h-7 w-64 bg-muted rounded mb-8" />
        <div className="grid grid-cols-3 gap-8 mb-8 pb-8 border-b border-border">
          {[0, 1, 2].map((i) => (
            <div key={i}>
              <div className="h-2 w-20 bg-muted rounded mb-3" />
              <div className="h-6 w-24 bg-muted rounded" />
            </div>
          ))}
        </div>
        <div className="h-3 w-32 bg-muted rounded mb-4" />
        <div className="space-y-2">
          {[0, 1, 2].map((i) => (
            <div key={i} className="h-3 bg-muted rounded w-full" />
          ))}
        </div>
      </div>
    );
  }

  // ── No Processes / Error State ─────────────────────────────────────────────
  if (isError || !rec) {
    return (
      <div className="bg-card border border-border rounded-2xl p-8 mb-8">
        <div className="flex flex-col items-center justify-center py-6 text-center">
          <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-4">
            <Zap className="w-8 h-8 text-muted-foreground" />
          </div>
          <h2 className="text-lg font-semibold text-foreground mb-2">
            No Recommendation Yet
          </h2>
          <p className="text-sm text-muted-foreground max-w-xs">
            Create your first Process and the Attention Kernel will recommend what to work on next.
          </p>
        </div>
      </div>
    );
  }

  // ── Recommendation State ───────────────────────────────────────────────────
  const deadlineLabel = rec.deadline
    ? new Date(rec.deadline).toLocaleDateString([], {
        month: "short",
        day: "numeric",
        year: "numeric",
      })
    : "No deadline";

  const confidencePct = Math.round(rec.confidence_score * 100);

  return (
    <div className="bg-card border border-border rounded-2xl p-8 mb-8">
      {/* Header */}
      <div className="mb-6">
        <p className="text-muted-foreground text-sm mb-2">
          Today&apos;s Recommended Time Slice
        </p>
        <h2 className="text-2xl font-semibold text-foreground">
          {rec.process_name}
        </h2>
      </div>

      {/* Details Grid */}
      <div className="grid grid-cols-3 gap-8 mb-8 pb-8 border-b border-border">
        <div>
          <p className="text-xs uppercase tracking-wide text-muted-foreground mb-2">
            Duration
          </p>
          <p className="text-lg font-semibold text-foreground">
            {rec.duration_hours >= 1
              ? `${rec.duration_hours}h`
              : `${Math.round(rec.duration_hours * 60)}m`}
          </p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-wide text-muted-foreground mb-2">
            Deadline
          </p>
          <p className="text-lg font-semibold text-foreground">{deadlineLabel}</p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-wide text-muted-foreground mb-2">
            Priority
          </p>
          <PriorityDots level={rec.priority} />
        </div>
      </div>

      {/* Reasons */}
      <div className="mb-8">
        <p className="text-xs uppercase tracking-wide text-muted-foreground mb-3">
          Why This?
        </p>
        <ul className="space-y-2">
          {rec.reasons.map((reason, i) => (
            <li key={i} className="flex gap-3 text-sm text-muted-foreground">
              <span className="text-primary font-bold">•</span>
              <span>{reason}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Confidence & Actions */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="w-12 h-12 rounded-lg bg-primary/10 border border-primary/30 flex items-center justify-center">
              <span className="text-primary font-semibold text-sm">{confidencePct}%</span>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Confidence</p>
              <p className="text-sm font-medium text-foreground">
                {confidencePct >= 85 ? "Very High" : confidencePct >= 70 ? "High" : "Moderate"}
              </p>
            </div>
          </div>
        </div>

        {/* CTA Buttons */}
        <div className="flex gap-3">
          <button
            className="px-4 py-2.5 rounded-lg text-sm font-medium text-muted-foreground bg-muted hover:bg-muted/80 transition-colors flex items-center gap-2"
            disabled
            title="Policy comparison available in Analytics"
          >
            <HelpCircle className="w-4 h-4" />
            {rec.policy_name}
          </button>
          <button
            onClick={() => recomputeMutation.mutate()}
            disabled={recomputeMutation.isPending}
            className="px-4 py-2.5 rounded-lg text-sm font-medium text-muted-foreground bg-muted hover:bg-muted/80 transition-colors flex items-center gap-2 disabled:opacity-60"
          >
            {recomputeMutation.isPending ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <RotateCcw className="w-4 h-4" />
            )}
            Regenerate
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
