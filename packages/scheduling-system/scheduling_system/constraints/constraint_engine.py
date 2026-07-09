from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Tuple
from scheduling_system.interfaces.constraint import IConstraint
from scheduling_system.models.time_slice import TimeSlice
from scheduling_system.models.execution_plan import ExecutionPlan
from scheduling_system.models.process import Process, ProcessLifecycle

class CalendarBlockageConstraint(IConstraint):
    @property
    def name(self) -> str:
        return "Calendar Blockage"

    @property
    def is_hard(self) -> bool:
        return True

    def validate_slice(self, time_slice: TimeSlice, context: Any) -> bool:
        """
        Context must contain 'blocked_intervals': List[Tuple[datetime, datetime]]
        """
        blocked_intervals = context.get("blocked_intervals", [])
        slice_start = time_slice.start_time
        slice_end = time_slice.end_time
        
        # Ensure slice timezone is set
        if slice_start.tzinfo is None:
            slice_start = slice_start.replace(tzinfo=timezone.utc)
        if slice_end.tzinfo is None:
            slice_end = slice_end.replace(tzinfo=timezone.utc)

        for b_start, b_end in blocked_intervals:
            if b_start.tzinfo is None:
                b_start = b_start.replace(tzinfo=timezone.utc)
            if b_end.tzinfo is None:
                b_end = b_end.replace(tzinfo=timezone.utc)
                
            # Check overlap
            if not (slice_end <= b_start or slice_start >= b_end):
                return False
                
        return True

    def validate_plan(self, plan: ExecutionPlan, context: Any) -> bool:
        for window in plan.execution_windows:
            if not self.validate_slice(window.time_slice, context):
                return False
        return True

class ProcessDependencyConstraint(IConstraint):
    @property
    def name(self) -> str:
        return "Process Dependency"

    @property
    def is_hard(self) -> bool:
        return True

    def validate_slice(self, time_slice: TimeSlice, context: Any) -> bool:
        """
        Context must contain 'processes': List[Process] representing the universe of processes
        """
        processes: List[Process] = context.get("processes", [])
        process_map = {p.id: p for p in processes}
        
        target_process = process_map.get(time_slice.process_id)
        if not target_process:
            return True
            
        # Check if any dependencies are incomplete
        for dep_id in target_process.dependency_ids:
            dep_process = process_map.get(dep_id)
            if dep_process:
                # If dependency has remaining effort or is not Completed, flag error
                if dep_process.remaining_effort_hours > 0 and dep_process.status != ProcessLifecycle.COMPLETED:
                    return False
        return True

    def validate_plan(self, plan: ExecutionPlan, context: Any) -> bool:
        # For validation of the plan, we must ensure order is respected:
        # A process cannot be scheduled BEFORE its incomplete dependencies are scheduled.
        processes: List[Process] = context.get("processes", [])
        process_map = {p.id: p for p in processes}
        
        scheduled_process_ids = set()
        for window in plan.execution_windows:
            p_id = window.time_slice.process_id
            target_process = process_map.get(p_id)
            if target_process:
                for dep_id in target_process.dependency_ids:
                    # If dependency is incomplete AND hasn't been scheduled earlier in this plan, it is invalid!
                    dep_process = process_map.get(dep_id)
                    if dep_process and dep_process.remaining_effort_hours > 0 and dep_id not in scheduled_process_ids:
                        return False
            scheduled_process_ids.add(p_id)
        return True

class MaxDailyHoursConstraint(IConstraint):
    @property
    def name(self) -> str:
        return "Max Daily Hours"

    @property
    def is_hard(self) -> bool:
        return True

    def validate_slice(self, time_slice: TimeSlice, context: Any) -> bool:
        # Single slice cannot exceed max daily hours (checked by planner)
        max_hours = context.get("max_daily_hours", 8.0)
        return time_slice.duration_hours <= max_hours

    def validate_plan(self, plan: ExecutionPlan, context: Any) -> bool:
        """
        Ensures the sum of duration in any single calendar day does not exceed max_daily_hours.
        """
        max_hours = context.get("max_daily_hours", 8.0)
        daily_hours: Dict[str, float] = {}
        
        for window in plan.execution_windows:
            ts = window.time_slice
            day_str = ts.start_time.astimezone(timezone.utc).strftime("%Y-%m-%d")
            daily_hours[day_str] = daily_hours.get(day_str, 0.0) + ts.duration_hours
            if daily_hours[day_str] > max_hours:
                return False
                
        return True

class ConstraintEngine:
    def __init__(self):
        self.constraints: List[IConstraint] = [
            CalendarBlockageConstraint(),
            ProcessDependencyConstraint(),
            MaxDailyHoursConstraint()
        ]

    def validate_slice(self, time_slice: TimeSlice, context: Dict[str, Any]) -> List[str]:
        """
        Returns a list of constraint names violated by the TimeSlice.
        """
        violations = []
        for c in self.constraints:
            if c.is_hard and not c.validate_slice(time_slice, context):
                violations.append(c.name)
        return violations

    def validate_plan(self, plan: ExecutionPlan, context: Dict[str, Any]) -> List[str]:
        """
        Returns a list of constraint names violated by the ExecutionPlan.
        """
        violations = []
        for c in self.constraints:
            if c.is_hard and not c.validate_plan(plan, context):
                violations.append(c.name)
        return violations
