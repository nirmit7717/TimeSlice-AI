from datetime import datetime, timezone, timedelta
import uuid
from typing import Dict, Any, List
from scheduling_system.models.execution_plan import ExecutionPlan, ExecutionWindow
from scheduling_system.models.time_slice import TimeSlice
from scheduling_system.planner.conflict_resolver import ConflictResolver
from .impact_analyzer import ImpactAnalyzer

class DynamicRescheduler:
    def __init__(self):
        self.conflict_resolver = ConflictResolver()
        self.impact_analyzer = ImpactAnalyzer()

    def reschedule(
        self,
        current_plan: ExecutionPlan,
        scheduling_event: Dict[str, Any],
        context: Dict[str, Any]
    ) -> ExecutionPlan:
        """
        Shifts slices locally to resolve overlaps with a new calendar event.
        Returns a new ExecutionPlan with updated windows.
        
        scheduling_event: {
            "event_type": str,         # e.g., "Calendar Interrupt"
            "start_time": datetime,
            "end_time": datetime
        }
        """
        event_start = scheduling_event["start_time"]
        event_end = scheduling_event["end_time"]
        if event_start.tzinfo is None:
            event_start = event_start.replace(tzinfo=timezone.utc)
        if event_end.tzinfo is None:
            event_end = event_end.replace(tzinfo=timezone.utc)

        # Clone context blocked intervals and append the new scheduling event
        blocked_intervals = list(context.get("blocked_intervals", []))
        blocked_intervals.append((event_start, event_end))
        updated_context = {**context, "blocked_intervals": blocked_intervals}

        orig_windows = current_plan.execution_windows
        if not orig_windows:
            return current_plan

        # Re-resolve slices starting from the first slice that overlaps or starts after the event
        slices_to_resolve = []
        untouched_windows = []

        for w in orig_windows:
            s = w.time_slice
            s_start = s.start_time
            if s_start.tzinfo is None:
                s_start = s_start.replace(tzinfo=timezone.utc)
                
            s_end = s_start + timedelta(hours=s.duration_hours)

            # If slice starts after the event start or overlaps with the event, we must reschedule it
            if s_end > event_start:
                # Deep copy the slice to avoid mutating original
                slices_to_resolve.append(TimeSlice(
                    id=s.id,
                    process_id=s.process_id,
                    start_time=s.start_time,
                    end_time=s.end_time,
                    duration_hours=s.duration_hours,
                    status=s.status,
                    reflection=s.reflection,
                    progress_gained=s.progress_gained
                ))
            else:
                untouched_windows.append(w)

        # Rerun conflict resolver on the slices that must be rescheduled
        resolved_slices = self.conflict_resolver.resolve_conflicts(slices_to_resolve, updated_context)

        # Reassemble the windows
        new_windows = list(untouched_windows)
        for s in resolved_slices:
            new_windows.append(ExecutionWindow(
                id=str(uuid.uuid4()),
                time_slice=s
            ))

        # Re-sort windows chronologically
        new_windows.sort(key=lambda w: w.time_slice.start_time)

        return ExecutionPlan(
            id=str(uuid.uuid4()),
            policy_name=current_plan.policy_name,
            time_quantum_hours=current_plan.time_quantum_hours,
            execution_windows=new_windows,
            created_at=datetime.now(timezone.utc)
        )
