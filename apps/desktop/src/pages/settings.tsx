import { useState } from "react";
import { Slider } from "../components/ui/slider";
import { TimeRangePicker } from "../components/ui/time-range-picker";
import { Toggle } from "../components/ui/toggle";
import { Shield, Clock, Brain, Calendar, Bell, CheckCircle2 } from "lucide-react";
import { usePreferencesStore } from "../stores/preferences-store";

export function SettingsPage() {
  const prefs = usePreferencesStore();

  // Temporary notification status
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Local state toggles for connected services
  const [googleConnected, setGoogleConnected] = useState(true);
  const [appleConnected, setAppleConnected] = useState(false);

  // Local state toggles for notification bots
  const [localNotifications, setLocalNotifications] = useState(true);
  const [telegramConnected, setTelegramConnected] = useState(false);
  const [telegramChatId, setTelegramChatId] = useState("");

  const handleSave = () => {
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 3000);
  };

  const handleReset = () => {
    prefs.resetToDefaults();
    setGoogleConnected(true);
    setAppleConnected(false);
    setLocalNotifications(true);
    setTelegramConnected(false);
    setTelegramChatId("");
  };

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

        {/* Hard/Soft Constraints Toggles */}
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
