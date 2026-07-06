import { cn } from "../../lib/utils";

interface HealthRingProps {
  value: number; // 0–100
  label: string;
  sublabel?: string;
  size?: number;
  strokeWidth?: number;
  className?: string;
}

export function HealthRing({
  value,
  label,
  sublabel,
  size = 120,
  strokeWidth = 8,
  className,
}: HealthRingProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (value / 100) * circumference;

  const getColor = (v: number) => {
    if (v >= 70) return "text-emerald-400";
    if (v >= 40) return "text-amber-400";
    return "text-red-400";
  };

  const getStrokeColor = (v: number) => {
    if (v >= 70) return "#22C55E";
    if (v >= 40) return "#F59E0B";
    return "#EF4444";
  };

  return (
    <div className={cn("flex flex-col items-center", className)}>
      <div className="relative" style={{ width: size, height: size }}>
        <svg className="transform -rotate-90" width={size} height={size}>
          {/* Background ring */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="var(--muted)"
            strokeWidth={strokeWidth}
          />
          {/* Value ring */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={getStrokeColor(value)}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className="transition-all duration-700 ease-out"
          />
        </svg>
        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={cn("text-xl font-bold", getColor(value))}>
            {value}%
          </span>
        </div>
      </div>
      <p className="text-sm font-medium text-foreground mt-3">{label}</p>
      {sublabel && (
        <p className="text-xs text-muted-foreground">{sublabel}</p>
      )}
    </div>
  );
}
