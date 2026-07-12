import { useQuery } from "@tanstack/react-query";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { HealthRing } from "./health-ring";
import { TrendingUp, TrendingDown, Minus, Loader2 } from "lucide-react";
import { apiClient } from "../../services/api-client";


interface ProcessMetric {
  processId: string;
  name?: string;
  attentionDebt: number;
  attentionEquity: number;
  deadlineRisk: string;
  completionVelocity: number;
  processHealth: number;
  healthStatus: string;
}

export function MetricsPanel() {
  // Query 1: Get process-specific metrics
  const { data: metrics, isLoading: loadingMetrics } = useQuery({
    queryKey: ["analytics-metrics"],
    queryFn: async () => {
      const res = await apiClient.get("/analytics/metrics");
      // Map to frontend-friendly snake_to_camel case structure
      return res.data.map((m: any) => ({
        processId: m.processId ?? m.process_id,
        name: m.name ?? `Process ${m.processId ?? m.process_id}`,
        attentionDebt: m.attentionDebt ?? m.attention_debt ?? 0.0,
        attentionEquity: m.attentionEquity ?? m.attention_equity ?? 0.0,
        deadlineRisk: m.deadlineRisk ?? m.deadline_risk ?? "Low",
        completionVelocity: m.completionVelocity ?? m.completion_velocity ?? 0.0,
        processHealth: m.processHealth ?? m.process_health ?? 100.0,
        healthStatus: m.healthStatus ?? m.health_status ?? "Excellent",
      })) as ProcessMetric[];
    },
    staleTime: 60 * 1000,
  });

  // Query 2: Get weekly digest summary
  const { data: weeklySummary, isLoading: loadingSummary } = useQuery({
    queryKey: ["weekly-summary"],
    queryFn: async () => {
      const res = await apiClient.get("/analytics/weekly-summary");
      return res.data;
    },
    staleTime: 60 * 1000,
  });

  if (loadingMetrics || loadingSummary) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  // Compute aggregate averages
  const totalProcesses = metrics?.length ?? 0;
  const avgDebt = totalProcesses
    ? metrics!.reduce((sum, m) => sum + m.attentionDebt, 0) / totalProcesses
    : 0.0;
  const avgEquity = totalProcesses
    ? metrics!.reduce((sum, m) => sum + m.attentionEquity, 0) / totalProcesses
    : 0.0;
  const criticalRiskCount = metrics?.filter((m) => m.deadlineRisk === "Critical" || m.deadlineRisk === "High").length ?? 0;
  const avgVelocity = totalProcesses
    ? metrics!.reduce((sum, m) => sum + m.completionVelocity, 0) / totalProcesses
    : 0.0;

  const keyCards = [
    {
      label: "Attention Debt",
      value: `${avgDebt.toFixed(1)}h`,
      trend: avgDebt > 5.0 ? "up" : "flat",
      trendValue: avgDebt > 5.0 ? "High neglect" : "Under control",
      trendColor: avgDebt > 5.0 ? "text-red-400" : "text-emerald-400",
    },
    {
      label: "Attention Equity",
      value: `${avgEquity.toFixed(1)}h`,
      trend: avgEquity > 10.0 ? "up" : "flat",
      trendValue: avgEquity > 10.0 ? "Strong momentum" : "Low momentum",
      trendColor: avgEquity > 10.0 ? "text-emerald-400" : "text-amber-400",
    },
    {
      label: "Critical Risks",
      value: `${criticalRiskCount} tasks`,
      trend: criticalRiskCount > 0 ? "up" : "flat",
      trendValue: criticalRiskCount > 0 ? "Action required" : "Stable",
      trendColor: criticalRiskCount > 0 ? "text-red-400" : "text-emerald-400",
    },
    {
      label: "Completion Velocity",
      value: `${avgVelocity.toFixed(1)}h/day`,
      trend: avgVelocity > 1.0 ? "up" : "flat",
      trendValue: avgVelocity > 1.0 ? "Productive" : "Stalled",
      trendColor: avgVelocity > 1.0 ? "text-emerald-400" : "text-amber-400",
    },
  ];

  // Map focus hours from summary for Recharts
  const focusChartData = weeklySummary?.weeklyFocusHours ?? [
    { day: "Mon", hours: 0 },
    { day: "Tue", hours: 0 },
    { day: "Wed", hours: 0 },
    { day: "Thu", hours: 0 },
    { day: "Fri", hours: 0 },
    { day: "Sat", hours: 0 },
    { day: "Sun", hours: 0 },
  ];

  return (
    <div className="space-y-8">
      {/* Health Rings */}
      <div>
        <h3 className="text-sm font-semibold text-foreground mb-6">
          Process Health
        </h3>
        {totalProcesses === 0 ? (
          <div className="bg-card border border-border rounded-xl p-8 text-center text-sm text-muted-foreground">
            No active processes to display.
          </div>
        ) : (
          <div className="grid grid-cols-4 gap-6">
            {metrics!.slice(0, 4).map((m) => (
              <HealthRing
                key={m.processId}
                value={Math.round(m.processHealth)}
                label={m.name || "Process"}
                sublabel={m.healthStatus}
              />
            ))}
          </div>
        )}
      </div>

      {/* Metric Cards */}
      <div>
        <h3 className="text-sm font-semibold text-foreground mb-4">
          Key Metrics
        </h3>
        <div className="grid grid-cols-4 gap-4">
          {keyCards.map((metric) => {
            const TrendIcon =
              metric.trend === "up"
                ? TrendingUp
                : metric.trend === "down"
                  ? TrendingDown
                  : Minus;
            return (
              <div
                key={metric.label}
                className="bg-card border border-border rounded-xl p-4"
              >
                <p className="text-xs text-muted-foreground mb-2">
                  {metric.label}
                </p>
                <p className="text-lg font-semibold text-foreground mb-1">
                  {metric.value}
                </p>
                <div
                  className={`flex items-center gap-1 ${metric.trendColor}`}
                >
                  <TrendIcon className="w-3 h-3" />
                  <span className="text-xs font-medium">
                    {metric.trendValue}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Velocity Chart */}
      <div>
        <h3 className="text-sm font-semibold text-foreground mb-4">
          Weekly focus hours trend
        </h3>
        <div className="bg-card border border-border rounded-xl p-6">
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={focusChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
              <XAxis
                dataKey="day"
                stroke="#A1A1A6"
                style={{ fontSize: "12px" }}
              />
              <YAxis stroke="#A1A1A6" style={{ fontSize: "12px" }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#111318",
                  border: "1px solid #27272A",
                  borderRadius: "8px",
                  boxShadow: "none",
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
        </div>
      </div>
    </div>
  );
}
