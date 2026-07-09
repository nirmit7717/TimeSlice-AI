import { NavLink } from "react-router-dom";
import {
  Zap,
  LayoutDashboard,
  Clock,
  BarChart3,
  Brain,
  Vault,
  Settings,
} from "lucide-react";

const menuItems = [
  { icon: LayoutDashboard, label: "Dashboard", href: "/" },
  { icon: Zap, label: "Processes", href: "/processes" },
  { icon: Clock, label: "Calendar", href: "/calendar" },
  { icon: BarChart3, label: "Analytics", href: "/analytics" },
  { icon: Brain, label: "Attention Kernel", href: "/kernel" },
  { icon: Vault, label: "Context Vault", href: "/vault" },
];

export function Sidebar() {
  return (
    <aside className="w-64 bg-card border-r border-border h-screen flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-border">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">TS</span>
          </div>
          <div>
            <h1 className="font-semibold text-sm text-foreground">
              TimeSlice AI
            </h1>
            <p className="text-xs text-muted-foreground">Attention Kernel</p>
          </div>
        </div>
      </div>

      {/* Menu */}
      <nav className="flex-1 px-4 py-6 space-y-2">
        {menuItems.map((item) => (
          <NavLink
            key={item.label}
            to={item.href}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg text-sm transition-colors group ${
                isActive
                  ? "bg-muted text-foreground"
                  : "text-muted-foreground hover:text-foreground hover:bg-muted"
              }`
            }
          >
            {({ isActive }) => (
              <>
                <item.icon
                  className={`w-5 h-5 transition-colors ${
                    isActive
                      ? "text-primary"
                      : "group-hover:text-primary"
                  }`}
                />
                <span>{item.label}</span>
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Settings Footer */}
      <div className="p-4 border-t border-border">
        <NavLink
          to="/settings"
          className={({ isActive }) =>
            `flex items-center gap-3 px-4 py-3 w-full rounded-lg text-sm transition-colors group ${
              isActive
                ? "bg-muted text-foreground"
                : "text-muted-foreground hover:text-foreground hover:bg-muted"
            }`
          }
        >
          {({ isActive }) => (
            <>
              <Settings
                className={`w-5 h-5 transition-colors ${
                  isActive ? "text-primary" : "group-hover:text-primary"
                }`}
              />
              <span>Settings</span>
            </>
          )}
        </NavLink>
      </div>
    </aside>
  );
}
