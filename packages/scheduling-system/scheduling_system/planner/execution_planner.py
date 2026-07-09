from datetime import datetime, timezone, timedelta
import uuid
from typing import List, Dict, Any
from scheduling_system.interfaces.policy import ISchedulerPolicy
from scheduling_system.models.process import Process
from scheduling_system.models.time_slice import TimeSlice
from scheduling_system.models.execution_plan import ExecutionPlan, ExecutionWindow
from .conflict_resolver import ConflictResolver

class ExecutionPlanner:
    def __init__(self):
        self.conflict_resolver = ConflictResolver()

    def plan(
        self,
        processes: List[Process],
        policy: ISchedulerPolicy,
        quantum_hours: float,
        available_hours: float,
        context: Dict[str, Any]
    ) -> ExecutionPlan:
        """
        Generates an ExecutionPlan by executing a policy, resolving calendar blocks,
        and validating capacity limits.
        """
        # 1. Generate Slices via Policy
        raw_slices = policy.generate_slices(processes, quantum_hours, available_hours)

        # 2. Resolve Overlaps with Blocked Intervals
        resolved_slices = self.conflict_resolver.resolve_conflicts(raw_slices, context)

        # 3. Handle Daily Working Capacity Limits (e.g. Max Daily Hours)
        max_daily_hours = context.get("max_daily_hours", 8.0)
        daily_durations: Dict[str, float] = {}
        final_slices = []

        for s in resolved_slices:
            day_str = s.start_time.astimezone(timezone.utc).strftime("%Y-%m-%d")
            current_day_total = daily_durations.get(day_str, 0.0)
            
            # If adding this slice violates daily capacity limits, shift it to next day
            if current_day_total + s.duration_hours > max_daily_hours:
                # Calculate next day start time
                next_day_start = s.start_time + timedelta(days=1)
                # Reset time to 9 AM (default preference or start of next day)
                next_day_start = next_day_start.replace(hour=9, minute=0, second=0, microsecond=0)
                
                # Shift slice
                dur = timedelta(hours=s.duration_hours)
                s.start_time = next_day_start
                s.end_time = next_day_start + dur
                
                # Rerun conflict resolver on this shifted slice relative to subsequent calendar blockages
                re_resolved = self.conflict_resolver.resolve_conflicts([s], context)
                if re_resolved:
                    s = re_resolved[0]
                    
                # Recompute day key
                day_str = s.start_time.astimezone(timezone.utc).strftime("%Y-%m-%d")
            
            daily_durations[day_str] = daily_durations.get(day_str, 0.0) + s.duration_hours
            final_slices.append(s)

        # 4. Wrap into Windows
        windows = [
            ExecutionWindow(id=str(uuid.uuid4()), time_slice=s)
            for s in final_slices
        ]

        return ExecutionPlan(
            id=str(uuid.uuid4()),
            policy_name=policy.name,
            time_quantum_hours=quantum_hours,
            execution_windows=windows,
            created_at=datetime.now(timezone.utc)
        )
