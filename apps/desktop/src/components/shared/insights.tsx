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

const focusData = [
  { day: "Mon", hours: 4.2 },
  { day: "Tue", hours: 5.1 },
  { day: "Wed", hours: 4.8 },
  { day: "Thu", hours: 6.2 },
  { day: "Fri", hours: 5.9 },
  { day: "Sat", hours: 3.1 },
  { day: "Sun", hours: 2.5 },
];

const debtData = [
  { week: "W1", debt: 8.5 },
  { week: "W2", debt: 12.3 },
  { week: "W3", debt: 9.8 },
  { week: "W4", debt: 17.8 },
];

export function Insights() {
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
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={focusData}>
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
          <div className="mt-6 p-4 rounded-lg bg-muted">
            <p className="text-xs text-muted-foreground mb-1">Average</p>
            <p className="text-lg font-semibold text-foreground">
              4.7 hours/day
            </p>
          </div>
        </div>

        {/* Attention Debt Trend */}
        <div className="bg-card border border-border rounded-xl p-6">
          <p className="text-xs uppercase tracking-wide text-muted-foreground mb-6 font-medium">
            Attention Debt Trend
          </p>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={debtData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
              <XAxis
                dataKey="week"
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
              <Bar dataKey="debt" fill="#F59E0B" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
          <div className="mt-6 p-4 rounded-lg bg-muted">
            <p className="text-xs text-muted-foreground mb-1">Current</p>
            <p className="text-lg font-semibold text-amber-400">17.8 hours</p>
          </div>
        </div>

        {/* Process Health */}
        <div className="bg-card border border-border rounded-xl p-6">
          <p className="text-xs uppercase tracking-wide text-muted-foreground mb-6 font-medium">
            Process Health
          </p>
          <div className="space-y-4">
            {[
              { name: "On Schedule", value: 65, color: "bg-emerald-400" },
              { name: "At Risk", value: 20, color: "bg-amber-400" },
              { name: "Overdue", value: 15, color: "bg-red-400" },
            ].map((item, idx) => (
              <div key={idx}>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-xs text-muted-foreground">
                    {item.name}
                  </span>
                  <span className="text-xs font-semibold text-foreground">
                    {item.value}%
                  </span>
                </div>
                <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                  <div
                    className={`h-full ${item.color}`}
                    style={{ width: `${item.value}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Focus Streak */}
        <div className="bg-card border border-border rounded-xl p-6">
          <p className="text-xs uppercase tracking-wide text-muted-foreground mb-6 font-medium">
            Focus Streak
          </p>
          <div className="flex items-center justify-between mb-6">
            <div>
              <p className="text-4xl font-bold text-primary">12</p>
              <p className="text-xs text-muted-foreground mt-1">
                consecutive days
              </p>
            </div>
            <div className="w-20 h-20 rounded-full bg-primary/10 border-2 border-primary flex items-center justify-center">
              <span className="text-2xl">🔥</span>
            </div>
          </div>
          <button className="w-full px-4 py-2 rounded-lg text-xs font-medium text-muted-foreground bg-muted hover:bg-muted/80 transition-colors">
            View Milestone
          </button>
        </div>
      </div>
    </div>
  );
}
