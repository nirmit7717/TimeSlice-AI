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
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

const velocityData = [
  { day: "Mon", velocity: 3.2 },
  { day: "Tue", velocity: 4.1 },
  { day: "Wed", velocity: 3.8 },
  { day: "Thu", velocity: 5.5 },
  { day: "Fri", velocity: 4.9 },
  { day: "Sat", velocity: 2.1 },
  { day: "Sun", velocity: 1.8 },
];

const metrics = [
  {
    label: "Attention Debt",
    value: "17.8h",
    trend: "up",
    trendValue: "+2.3h",
    trendColor: "text-red-400",
  },
  {
    label: "Attention Equity",
    value: "53.5h",
    trend: "up",
    trendValue: "+4.2h",
    trendColor: "text-emerald-400",
  },
  {
    label: "Deadline Risk",
    value: "2 processes",
    trend: "flat",
    trendValue: "Stable",
    trendColor: "text-amber-400",
  },
  {
    label: "Completion Velocity",
    value: "3.6h/day",
    trend: "up",
    trendValue: "+0.4h",
    trendColor: "text-emerald-400",
  },
];

export function MetricsPanel() {
  return (
    <div className="space-y-8">
      {/* Health Rings */}
      <div>
        <h3 className="text-sm font-semibold text-foreground mb-6">
          Process Health
        </h3>
        <div className="grid grid-cols-4 gap-6">
          <HealthRing value={82} label="Backend Scheduler" sublabel="Healthy" />
          <HealthRing value={45} label="Azure AZ-900" sublabel="At Risk" />
          <HealthRing value={25} label="Q4 Planning" sublabel="Critical" />
          <HealthRing value={68} label="Code Review" sublabel="Fair" />
        </div>
      </div>

      {/* Metric Cards */}
      <div>
        <h3 className="text-sm font-semibold text-foreground mb-4">
          Key Metrics
        </h3>
        <div className="grid grid-cols-4 gap-4">
          {metrics.map((metric) => {
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
          Completion Velocity
        </h3>
        <div className="bg-card border border-border rounded-xl p-6">
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={velocityData}>
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
                dataKey="velocity"
                stroke="#22C55E"
                strokeWidth={2}
                dot={{ fill: "#22C55E", r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
