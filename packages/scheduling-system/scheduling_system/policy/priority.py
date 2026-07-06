from datetime import datetime, timedelta, timezone
import uuid
from typing import List
from scheduling_system.interfaces.policy import ISchedulerPolicy
from scheduling_system.models.process import Process, ProcessLifecycle
from scheduling_system.models.time_slice import TimeSlice, SliceStatus

class PriorityPolicy(ISchedulerPolicy):
    @property
    def name(self) -> str:
        return "Priority"

    def generate_slices(
        self, 
        processes: List[Process], 
        quantum_hours: float, 
        available_hours: float
    ) -> List[TimeSlice]:
        """
        Generates a scheduled list of time slices for the given processes, sorted by priority (highest first)
        and attention debt (highest first).
        
        Args:
            processes: A list of Process domain models to schedule.
            quantum_hours: Time quantum size (slice duration limit) in hours.
            available_hours: Total available capacity time budget in hours.
            
        Returns:
            A list of generated TimeSlice records.
        """
        # Filter active processes with remaining effort > 0
        active = [
            p for p in processes 
            if p.remaining_effort_hours > 0 
            and p.status not in (ProcessLifecycle.COMPLETED, ProcessLifecycle.ARCHIVED)
        ]
        
        # Sort by priority (5 down to 1), then attention debt (descending)
        active.sort(key=lambda x: (x.priority, x.attention_debt), reverse=True)
        
        if not active or available_hours <= 0 or quantum_hours <= 0:
            return []

        slices = []
        elapsed_hours = 0.0
        start_time = datetime.now(timezone.utc)
        
        remaining_efforts = {p.id: p.remaining_effort_hours for p in active}
        
        for p in active:
            while remaining_efforts[p.id] > 0 and elapsed_hours < available_hours:
                # Calculate slice duration
                slice_dur = min(quantum_hours, remaining_efforts[p.id], available_hours - elapsed_hours)
                if slice_dur <= 0:
                    break
                    
                slice_start = start_time + timedelta(hours=elapsed_hours)
                slice_end = slice_start + timedelta(hours=slice_dur)
                
                slices.append(TimeSlice(
                    id=str(uuid.uuid4()),
                    process_id=p.id,
                    start_time=slice_start,
                    end_time=slice_end,
                    duration_hours=slice_dur,
                    status=SliceStatus.SCHEDULED
                ))
                
                remaining_efforts[p.id] -= slice_dur
                elapsed_hours += slice_dur
                
        return slices
