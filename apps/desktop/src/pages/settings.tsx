import { useState } from "react";
import { Slider } from "../components/ui/slider";
import { TimeRangePicker } from "../components/ui/time-range-picker";
import { Toggle } from "../components/ui/toggle";
import { Shield, Clock, Brain } from "lucide-react";

export function SettingsPage() {
  // Constraint settings state
  const [workStart, setWorkStart] = useState("09:00");
  const [workEnd, setWorkEnd] = useState("18:00");
  const [focusStart, setFocusStart] = useState("09:00");
  const [focusEnd, setFocusEnd] = useState("12:00");
  const [restStart, setRestStart] = useState("12:00");
  const [restEnd, setRestEnd] = useState("13:00");

  const [maxSessionLength, setMaxSessionLength] = useState(90);
  const [minBreakBetween, setMinBreakBetween] = useState(15);
  const [maxDailyFocus, setMaxDailyFocus] = useState(6);
  const [contextSwitchPenalty, setContextSwitchPenalty] = useState(30);

  const [respectCalendar, setRespectCalendar] = useState(true);
  const [allowWeekends, setAllowWeekends] = useState(false);
  const [enforceRestPeriods, setEnforceRestPeriods] = useState(true);
  const [adaptiveQuantum, setAdaptiveQuantum] = useState(true);

  return (
    <div className="p-8 max-w-3xl">
      <div className="mb-8">
        <h1 className="text-3xl font-semibold text-foreground">Settings</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Configure scheduling constraints and preferences
        </p>
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
              startTime={workStart}
              endTime={workEnd}
              onStartChange={setWorkStart}
              onEndChange={setWorkEnd}
            />
            <TimeRangePicker
              label="Peak Focus Window"
              startTime={focusStart}
              endTime={focusEnd}
              onStartChange={setFocusStart}
              onEndChange={setFocusEnd}
            />
            <TimeRangePicker
              label="Rest Period"
              startTime={restStart}
              endTime={restEnd}
              onStartChange={setRestStart}
              onEndChange={setRestEnd}
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
              value={maxSessionLength}
              min={15}
              max={240}
              step={15}
              unit=" min"
              onChange={setMaxSessionLength}
            />
            <Slider
              label="Min Break Between Sessions"
              value={minBreakBetween}
              min={5}
              max={60}
              step={5}
              unit=" min"
              onChange={setMinBreakBetween}
            />
            <Slider
              label="Max Daily Focus Hours"
              value={maxDailyFocus}
              min={2}
              max={12}
              step={1}
              unit="h"
              onChange={setMaxDailyFocus}
            />
            <Slider
              label="Context Switch Penalty"
              value={contextSwitchPenalty}
              min={5}
              max={60}
              step={5}
              unit=" min"
              onChange={setContextSwitchPenalty}
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
              checked={respectCalendar}
              onChange={setRespectCalendar}
            />
            <Toggle
              label="Allow Weekend Scheduling"
              description="Include weekends in execution plan generation"
              checked={allowWeekends}
              onChange={setAllowWeekends}
            />
            <Toggle
              label="Enforce Rest Periods"
              description="Block scheduling during defined rest periods (hard constraint)"
              checked={enforceRestPeriods}
              onChange={setEnforceRestPeriods}
            />
            <Toggle
              label="Adaptive Time Quantum"
              description="Let the AI adjust session durations based on your patterns"
              checked={adaptiveQuantum}
              onChange={setAdaptiveQuantum}
            />
          </div>
        </section>

        {/* Save */}
        <div className="flex gap-3">
          <button className="px-6 py-2.5 rounded-lg text-sm font-semibold bg-primary text-primary-foreground hover:bg-primary/90 transition-colors">
            Save Preferences
          </button>
          <button className="px-4 py-2.5 rounded-lg text-sm font-medium text-muted-foreground bg-muted hover:bg-muted/80 transition-colors">
            Reset to Defaults
          </button>
        </div>
      </div>
    </div>
  );
}
