import { useState, useEffect } from "react";
import { Slider } from "../components/ui/slider";
import { TimeRangePicker } from "../components/ui/time-range-picker";
import { Toggle } from "../components/ui/toggle";
import { Shield, Clock, Brain, Calendar, Bell, CheckCircle2, Sparkles, TrendingUp, Zap, Target } from "lucide-react";
import { usePreferencesStore } from "../stores/preferences-store";
import { useAdaptiveStore } from "../stores/adaptive-store";

export function SettingsPage() {
  const prefs = usePreferencesStore();
  const adaptive = useAdaptiveStore();

  // Temporary notification status
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Local state toggles for connected services
  const [googleConnected, setGoogleConnected] = useState(true);
  const [appleConnected, setAppleConnected] = useState(false);

  // Local state toggles for notification bots
  const [localNotifications, setLocalNotifications] = useState(true);
  const [telegramConnected, setTelegramConnected] = useState(false);
  const [telegramChatId, setTelegramChatId] = useState("");

  // Adaptive overrides (local pending state before PUT)
  const [pendingPolicy, setPendingPolicy] = useState<string | null>(null);
  const [pendingQuantum, setPendingQuantum] = useState<number | null>(null);

  // Load adaptive data on mount
  useEffect(() => {
    adaptive.fetchProfile();
    adaptive.fetchOperatorModel();
  }, []);

  // Sync state when profile loads
  useEffect(() => {
    if (adaptive.profile) {
      setLocalNotifications(adaptive.profile.local_notifications ?? true);
      setTelegramConnected(adaptive.profile.telegram_connected ?? false);
      setTelegramChatId(adaptive.profile.telegram_chat_id ?? "");
    }
  }, [adaptive.profile]);

  const handleSave = async () => {
    // Save scheduling and notification preferences locally
    await adaptive.overrideProfile({
      ...(pendingPolicy !== null ? { preferred_policy: pendingPolicy } : {}),
      ...(pendingQuantum !== null ? { preferred_quantum_hours: pendingQuantum } : {}),
      local_notifications: localNotifications,
      telegram_connected: telegramConnected,
      telegram_chat_id: telegramChatId,
    });
    setPendingPolicy(null);
    setPendingQuantum(null);
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 3000);
  };

  const [testSent, setTestSent] = useState<boolean>(false);
  const [testError, setTestError] = useState<string | null>(null);

  const handleSendTest = async () => {
    setTestError(null);
    setTestSent(true);
    try {
      const res = await fetch("http://localhost:8000/api/v1/notifications/test", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: "TimeSlice AI Test Notification",
          message: "Your Telegram Bot alert system is working perfectly!",
          priority: "normal",
          channels: telegramConnected ? ["desktop", "telegram"] : ["desktop"]
        })
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to deliver test notification");
      }
    } catch (err) {
      setTestError(String(err));
    } finally {
      setTimeout(() => setTestSent(false), 3000);
    }
  };

  const handleReset = () => {
    prefs.resetToDefaults();
    setGoogleConnected(true);
    setAppleConnected(false);
    setLocalNotifications(true);
    setTelegramConnected(false);
    setTelegramChatId("");
    setPendingPolicy(null);
    setPendingQuantum(null);
  };

  // Derived display values
  const displayPolicy = pendingPolicy ?? adaptive.profile?.preferred_policy ?? "round_robin";
  const displayQuantum = pendingQuantum ?? adaptive.profile?.preferred_quantum_hours ?? 2.0;
  const model = adaptive.operatorModel;

  const policyLabels: Record<string, string> = {
    round_robin: "Round Robin",
    priority: "Priority-First",
    sjf: "Shortest Job First",
    edf: "Earliest Deadline First",
  };

  const quantumOptions = [0.5, 1.0, 2.0, 3.0, 4.0];


  return (
    <div className="p-8 max-w-3xl">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-foreground">Settings</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Configure scheduling constraints and system preferences
          </p>
        </div>
        {saveSuccess && (
          <div className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 rounded-lg text-xs font-semibold animate-fade-in">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Preferences Saved
          </div>
        )}
      </div>

      <div className="space-y-8">
        {/* Schedule Constraints */}
        <section className="bg-card border border-border rounded-xl p-6">
          <div className="flex items-center gap-2 mb-6">
            <Clock className="w-5 h-5 text-primary" />
            <h2 className="text-sm font-semibold text-foreground">
              Time Constraints
            </h2>
          </div>

          <div className="space-y-6">
            <TimeRangePicker
              label="Working Hours"
              startTime={prefs.workStartTime}
              endTime={prefs.workEndTime}
              onStartChange={(start) => prefs.setWorkHours(start, prefs.workEndTime)}
              onEndChange={(end) => prefs.setWorkHours(prefs.workStartTime, end)}
            />
            <TimeRangePicker
              label="Peak Focus Window"
              startTime={prefs.focusStartTime}
              endTime={prefs.focusEndTime}
              onStartChange={(start) => prefs.setFocusWindow(start, prefs.focusEndTime)}
              onEndChange={(end) => prefs.setFocusWindow(prefs.focusStartTime, end)}
            />
            <TimeRangePicker
              label="Rest Period"
              startTime={prefs.restStartTime}
              endTime={prefs.restEndTime}
              onStartChange={(start) => prefs.setRestPeriod(start, prefs.restEndTime)}
              onEndChange={(end) => prefs.setRestPeriod(prefs.restStartTime, end)}
            />
          </div>
        </section>

        {/* Quantum & Session Limits */}
        <section className="bg-card border border-border rounded-xl p-6">
          <div className="flex items-center gap-2 mb-6">
            <Brain className="w-5 h-5 text-secondary" />
            <h2 className="text-sm font-semibold text-foreground">
              Attention Parameters
            </h2>
          </div>

          <div className="space-y-6">
            <Slider
              label="Max Session Length"
              value={prefs.maxSessionMinutes}
              min={15}
              max={240}
              step={15}
              unit=" min"
              onChange={(v) => prefs.setMaxSession(v)}
            />
            <Slider
              label="Min Break Between Sessions"
              value={prefs.minBreakMinutes}
              min={5}
              max={60}
              step={5}
              unit=" min"
              onChange={(v) => prefs.setMinBreak(v)}
            />
            <Slider
              label="Max Daily Focus Hours"
              value={prefs.maxDailyFocusHours}
              min={2}
              max={12}
              step={1}
              unit="h"
              onChange={(v) => prefs.setMaxDailyFocus(v)}
            />
            <Slider
              label="Context Switch Penalty"
              value={prefs.contextSwitchPenaltyMinutes}
              min={5}
              max={60}
              step={5}
              unit=" min"
              onChange={(v) => prefs.setContextSwitchPenalty(v)}
            />
          </div>
        </section>

        {/* Constraint Rules */}
        <section className="bg-card border border-border rounded-xl p-6">
          <div className="flex items-center gap-2 mb-6">
            <Shield className="w-5 h-5 text-emerald-400" />
            <h2 className="text-sm font-semibold text-foreground">
              Constraint Rules
            </h2>
          </div>

          <div className="space-y-5">
            <Toggle
              label="Respect Calendar Events"
              description="Never schedule over existing calendar events (hard constraint)"
              checked={prefs.respectCalendarEvents}
              onChange={(v) => prefs.setConstraintRule("respectCalendarEvents", v)}
            />
            <Toggle
              label="Allow Weekend Scheduling"
              description="Include weekends in execution plan generation"
              checked={prefs.allowWeekends}
              onChange={(v) => prefs.setConstraintRule("allowWeekends", v)}
            />
            <Toggle
              label="Enforce Rest Periods"
              description="Block scheduling during defined rest periods (hard constraint)"
              checked={prefs.enforceRestPeriods}
              onChange={(v) => prefs.setConstraintRule("enforceRestPeriods", v)}
            />
            <Toggle
              label="Adaptive Time Quantum"
              description="Let the AI adjust session durations based on your patterns"
              checked={prefs.adaptiveQuantum}
              onChange={(v) => prefs.setConstraintRule("adaptiveQuantum", v)}
            />
          </div>
        </section>

        {/* ── Adaptive Intelligence ─────────────────────────────────────── */}
        <section className="bg-card border border-border rounded-xl p-6 relative overflow-hidden">
          {/* Ambient gradient accent */}
          <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-secondary/5 pointer-events-none" />

          <div className="flex items-center gap-2 mb-2 relative">
            <Sparkles className="w-5 h-5 text-primary" />
            <h2 className="text-sm font-semibold text-foreground">Adaptive Intelligence</h2>
            <span className="ml-auto px-2 py-0.5 bg-primary/10 text-primary border border-primary/20 rounded-full text-[10px] font-bold uppercase tracking-wide">
              LinUCB Active
            </span>
          </div>
          <p className="text-xs text-muted-foreground mb-6 relative">
            The bandit engine learns from each session outcome and continuously refines your optimal scheduling strategy.
          </p>

          {/* Operator Model Stats */}
          {model && (
            <div className="grid grid-cols-2 gap-3 mb-6 relative">
              <div className="bg-background/60 border border-border/60 rounded-lg p-3">
                <div className="flex items-center gap-1.5 mb-1">
                  <TrendingUp className="w-3.5 h-3.5 text-primary" />
                  <span className="text-[10px] uppercase tracking-wide text-muted-foreground font-semibold">Velocity</span>
                </div>
                <div className="text-lg font-bold text-foreground">{model.velocity_score.toFixed(1)}h/day</div>
                <div className="text-[10px] text-muted-foreground">avg focus hours completed</div>
              </div>
              <div className="bg-background/60 border border-border/60 rounded-lg p-3">
                <div className="flex items-center gap-1.5 mb-1">
                  <Target className="w-3.5 h-3.5 text-secondary" />
                  <span className="text-[10px] uppercase tracking-wide text-muted-foreground font-semibold">Consistency</span>
                </div>
                <div className="text-lg font-bold text-foreground">{(model.consistency_score * 100).toFixed(0)}%</div>
                <div className="text-[10px] text-muted-foreground">{model.total_slices_completed} completed / {model.total_slices_abandoned} abandoned</div>
              </div>
              <div className="bg-background/60 border border-border/60 rounded-lg p-3">
                <div className="flex items-center gap-1.5 mb-1">
                  <Brain className="w-3.5 h-3.5 text-amber-400" />
                  <span className="text-[10px] uppercase tracking-wide text-muted-foreground font-semibold">Focus Avg</span>
                </div>
                <div className="text-lg font-bold text-foreground">{model.focus_duration_avg.toFixed(1)}h</div>
                <div className="text-[10px] text-muted-foreground">avg session duration</div>
              </div>
              <div className="bg-background/60 border border-border/60 rounded-lg p-3">
                <div className="flex items-center gap-1.5 mb-1">
                  <Zap className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-[10px] uppercase tracking-wide text-muted-foreground font-semibold">Switch Tol.</span>
                </div>
                <div className="text-lg font-bold text-foreground">{(model.switch_tolerance * 100).toFixed(0)}%</div>
                <div className="text-[10px] text-muted-foreground">context-switching tolerance</div>
              </div>
            </div>
          )}

          {/* Learned Policy Override */}
          <div className="relative space-y-4">
            <div>
              <label className="block text-[10px] uppercase tracking-wide text-muted-foreground mb-2 font-semibold">
                Preferred Scheduling Policy
                <span className="ml-2 text-primary font-normal normal-case">learned</span>
              </label>
              <div className="flex flex-wrap gap-2">
                {Object.entries(policyLabels).map(([key, label]) => (
                  <button
                    key={key}
                    onClick={() => setPendingPolicy(key)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                      displayPolicy === key
                        ? "bg-primary text-primary-foreground border-primary shadow-lg shadow-primary/20"
                        : "bg-muted text-muted-foreground border-border hover:border-primary/40 hover:text-foreground"
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-[10px] uppercase tracking-wide text-muted-foreground mb-2 font-semibold">
                Preferred Time Quantum
                <span className="ml-2 text-primary font-normal normal-case">learned — {displayQuantum}h sessions</span>
              </label>
              <div className="flex gap-2">
                {quantumOptions.map((q) => (
                  <button
                    key={q}
                    onClick={() => setPendingQuantum(q)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                      Math.abs(displayQuantum - q) < 0.01
                        ? "bg-secondary text-secondary-foreground border-secondary shadow-lg shadow-secondary/20"
                        : "bg-muted text-muted-foreground border-border hover:border-secondary/40 hover:text-foreground"
                    }`}
                  >
                    {q === 0.5 ? "30m" : `${q}h`}
                  </button>
                ))}
              </div>
            </div>

            {(pendingPolicy !== null || pendingQuantum !== null) && (
              <div className="flex items-center gap-2 p-2.5 bg-amber-500/10 border border-amber-500/20 rounded-lg">
                <div className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
                <span className="text-[11px] text-amber-400 font-medium">
                  Unsaved override pending — click Save Preferences to apply
                </span>
              </div>
            )}
          </div>
        </section>

        {/* Connected Calendars (Sprint 17) */}
        <section className="bg-card border border-border rounded-xl p-6">
          <div className="flex items-center gap-2 mb-6">
            <Calendar className="w-5 h-5 text-primary" />
            <h2 className="text-sm font-semibold text-foreground">
              Connected Calendars
            </h2>
          </div>

          <div className="space-y-5">
            <Toggle
              label="Google Calendar Synchronization"
              description="Sync focus slot blockages from developer@gmail.com"
              checked={googleConnected}
              onChange={setGoogleConnected}
            />
            <Toggle
              label="Apple Calendar Integration"
              description="Import busy blocks from iCloud calendars"
              checked={appleConnected}
              onChange={setAppleConnected}
            />
          </div>
        </section>

        {/* Notifications Config (Sprint 18) */}
        <section className="bg-card border border-border rounded-xl p-6">
          <div className="flex items-center gap-2 mb-6">
            <Bell className="w-5 h-5 text-secondary" />
            <h2 className="text-sm font-semibold text-foreground">
              Notifications & Alerts
            </h2>
          </div>

          <div className="space-y-5">
            <Toggle
              label="Local Notifications"
              description="Send desktop notifications for time slice focus reminders"
              checked={localNotifications}
              onChange={setLocalNotifications}
            />
            <div className="border-t border-border pt-4 mt-2">
              <Toggle
                label="Telegram Alert Bot"
                description="Receive reminders via the Telegram notifications bot"
                checked={telegramConnected}
                onChange={setTelegramConnected}
              />
              {telegramConnected && (
                <div className="mt-4 pl-4 border-l-2 border-primary/30">
                  <label className="block text-[10px] uppercase tracking-wide text-muted-foreground mb-1.5 font-semibold">
                    Telegram Chat ID
                  </label>
                  <input
                    type="text"
                    value={telegramChatId}
                    onChange={(e) => setTelegramChatId(e.target.value)}
                    placeholder="e.g., 579294711"
                    className="w-full max-w-xs bg-input border border-border rounded-lg px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                  />
                  <p className="text-[10px] text-muted-foreground mt-1">
                    Send `/start` to `@TimeSliceNotificationsBot` to retrieve your Chat ID.
                  </p>
                  <button
                    onClick={handleSendTest}
                    disabled={testSent}
                    className="mt-3 px-3 py-1.5 border border-primary/30 hover:border-primary/60 text-primary text-[10px] font-semibold uppercase tracking-wider rounded-lg transition-colors bg-primary/5 disabled:opacity-50"
                  >
                    {testSent ? "Dispatched..." : "Send Test Notification"}
                  </button>
                  {testError && (
                    <p className="text-[10px] text-rose-400 mt-1 font-semibold">
                      {testError}
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>
        </section>

        {/* Save/Reset Controls */}
        <div className="flex gap-3 pt-4">
          <button
            onClick={handleSave}
            className="px-6 py-2.5 rounded-lg text-sm font-semibold bg-primary text-primary-foreground hover:bg-primary/90 transition-colors shadow-lg shadow-primary/10"
          >
            Save Preferences
          </button>
          <button
            onClick={handleReset}
            className="px-4 py-2.5 rounded-lg text-sm font-medium text-muted-foreground bg-muted hover:bg-muted/80 transition-colors"
          >
            Reset to Defaults
          </button>
        </div>
      </div>
    </div>
  );
}
