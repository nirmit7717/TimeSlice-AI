import { useQuery } from "@tanstack/react-query";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";
import { apiClient } from "../../services/api-client";


// ─── Skeleton placeholder ─────────────────────────────────────────────────────
function ChartSkeleton({ height = 200 }: { height?: number }) {
  return (
    <div
      className="animate-pulse bg-muted rounded-lg"
      style={{ height: `${height}px` }}
    />
  );
}

function StatSkeleton() {
  return (
    <div className="mt-6 p-4 rounded-lg bg-muted animate-pulse">
      <div className="h-2 w-16 bg-muted-foreground/30 rounded mb-2" />
      <div className="h-5 w-24 bg-muted-foreground/30 rounded" />
    </div>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────
export function Insights() {
  // Fetch per-process metrics from backend (computes debt, equity, health)
  const { data: metrics, isLoading: metricsLoading } = useQuery({
    queryKey: ["scheduling-metrics"],
    queryFn: async () => {
      const res = await apiClient.get("/scheduler/metrics");
      return res.data as Array<{
        id: string;
        name: string;
        attention_debt?: number;
        attentionDebt?: number;
        attention_equity?: number;
        attentionEquity?: number;
        health_score?: number;
        healthScore?: number;
        progress?: number;
      }>;
    },
    staleTime: 2 * 60 * 1000,
    retry: false,
  });

  const isLoading = metricsLoading;

  // ── Derived chart data ───────────────────────────────────────────────────────
  // Weekly focus hours: not yet tracked per-day, so show a placeholder chart
  // that will populate once the execution system is live (Phase 3)
  const focusData = [
    { day: "Mon", hours: 0 },
    { day: "Tue", hours: 0 },
    { day: "Wed", hours: 0 },
    { day: "Thu", hours: 0 },
    { day: "Fri", hours: 0 },
    { day: "Sat", hours: 0 },
    { day: "Sun", hours: 0 },
  ];

  // Attention Debt per process (top 4)
  const debtData = metrics
    ? metrics
        .slice(0, 4)
        .map((p) => ({
          name: p.name.slice(0, 12) + (p.name.length > 12 ? "…" : ""),
          debt: Math.round((p.attention_debt ?? p.attentionDebt ?? 0) * 10) / 10,
        }))
    : [];

  // Process health distribution
  const excellent = metrics ? metrics.filter((p) => (p.health_score ?? p.healthScore ?? 100) >= 75).length : 0;
  const atRisk = metrics ? metrics.filter((p) => {
    const h = p.health_score ?? p.healthScore ?? 100;
    return h >= 40 && h < 75;
  }).length : 0;
  const critical = metrics ? metrics.filter((p) => (p.health_score ?? p.healthScore ?? 100) < 40).length : 0;
  const total = metrics?.length ?? 1;

  const healthBars = [
    { name: "On Schedule", value: Math.round((excellent / total) * 100), color: "bg-emerald-400" },
    { name: "At Risk", value: Math.round((atRisk / total) * 100), color: "bg-amber-400" },
    { name: "Critical", value: Math.round((critical / total) * 100), color: "bg-red-400" },
  ];

  const avgDebt =
    metrics && metrics.length
      ? metrics.reduce((sum, p) => sum + (p.attention_debt ?? p.attentionDebt ?? 0), 0) / metrics.length
      : 0;

  return (
    <div>
      <h3 className="text-sm font-semibold text-foreground mb-6">
        Weekly Insights
      </h3>

      <div className="grid grid-cols-2 gap-6">
        {/* Weekly Focus Hours */}
        <div className="bg-card border border-border rounded-xl p-6">
          <p className="text-xs uppercase tracking-wide text-muted-foreground mb-6 font-medium">
            Weekly Focus Hours
          </p>
          {isLoading ? (
            <ChartSkeleton />
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={focusData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
                <XAxis dataKey="day" stroke="#A1A1A6" style={{ fontSize: "12px" }} />
                <YAxis stroke="#A1A1A6" style={{ fontSize: "12px" }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#111318",
                    border: "1px solid #27272A",
                    borderRadius: "8px",
                  }}
                  labelStyle={{ color: "#FAFAFA" }}
                />
                <Line
                  type="monotone"
                  dataKey="hours"
                  stroke="#4F7CFF"
                  strokeWidth={2}
                  dot={{ fill: "#4F7CFF", r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
          <div className="mt-6 p-4 rounded-lg bg-muted">
            <p className="text-xs text-muted-foreground mb-1">Average</p>
            <p className="text-lg font-semibold text-foreground">
              {isLoading ? "—" : "0.0 hours/day"}
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Tracking starts once you log Time Slices
            </p>
          </div>
        </div>

        {/* Attention Debt by Process */}
        <div className="bg-card border border-border rounded-xl p-6">
          <p className="text-xs uppercase tracking-wide text-muted-foreground mb-6 font-medium">
            Attention Debt by Process
          </p>
          {isLoading ? (
            <ChartSkeleton />
          ) : debtData.length === 0 ? (
            <div className="flex items-center justify-center h-[200px] text-muted-foreground text-sm">
              No processes yet
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={debtData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
                <XAxis dataKey="name" stroke="#A1A1A6" style={{ fontSize: "10px" }} />
                <YAxis stroke="#A1A1A6" style={{ fontSize: "12px" }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#111318",
                    border: "1px solid #27272A",
                    borderRadius: "8px",
                  }}
                  labelStyle={{ color: "#FAFAFA" }}
                />
                <Bar dataKey="debt" fill="#F59E0B" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
          {isLoading ? (
            <StatSkeleton />
          ) : (
            <div className="mt-6 p-4 rounded-lg bg-muted">
              <p className="text-xs text-muted-foreground mb-1">Avg. Debt</p>
              <p className="text-lg font-semibold text-amber-400">
                {avgDebt.toFixed(1)} hrs
              </p>
            </div>
          )}
        </div>

        {/* Process Health */}
        <div className="bg-card border border-border rounded-xl p-6">
          <p className="text-xs uppercase tracking-wide text-muted-foreground mb-6 font-medium">
            Process Health
          </p>
          {isLoading ? (
            <div className="space-y-4">
              {[0, 1, 2].map((i) => (
                <div key={i} className="animate-pulse">
                  <div className="h-2 w-24 bg-muted rounded mb-2" />
                  <div className="h-1.5 bg-muted rounded-full" />
                </div>
              ))}
            </div>
          ) : metrics && metrics.length === 0 ? (
            <p className="text-sm text-muted-foreground">Create processes to track health</p>
          ) : (
            <div className="space-y-4">
              {healthBars.map((item, idx) => (
                <div key={idx}>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-xs text-muted-foreground">{item.name}</span>
                    <span className="text-xs font-semibold text-foreground">{item.value}%</span>
                  </div>
                  <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                    <div
                      className={`h-full ${item.color} transition-all duration-500`}
                      style={{ width: `${item.value}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Focus Streak */}
        <div className="bg-card border border-border rounded-xl p-6">
          <p className="text-xs uppercase tracking-wide text-muted-foreground mb-6 font-medium">
            Focus Streak
          </p>
          {isLoading ? (
            <div className="animate-pulse">
              <div className="h-10 w-16 bg-muted rounded mb-2" />
              <div className="h-3 w-24 bg-muted rounded" />
            </div>
          ) : (
            <>
              <div className="flex items-center justify-between mb-6">
                <div>
                  <p className="text-4xl font-bold text-primary">0</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    consecutive days
                  </p>
                </div>
                <div className="w-20 h-20 rounded-full bg-primary/10 border-2 border-primary/30 flex items-center justify-center">
                  <span className="text-2xl">🎯</span>
                </div>
              </div>
              <p className="text-xs text-muted-foreground">
                Complete your first Time Slice to start your streak!
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
