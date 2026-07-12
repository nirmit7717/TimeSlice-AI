from datetime import datetime, timezone, timedelta
from typing import List
from scheduling_system.models.time_slice import TimeSlice

class CompletionVelocityCalculator:
    def calculate_velocity(self, completed_slices: List[TimeSlice], rolling_window_days: int = 7) -> float:
        """
        Calculates the completion velocity in hours/day over the rolling window.
        """
        if not completed_slices:
            return 0.0

        now = datetime.now(timezone.utc)
        cutoff_date = now - timedelta(days=rolling_window_days)
        
        # Filter completed slices within the rolling window
        recent_slices = []
        for s in completed_slices:
            end_time = s.end_time
            if end_time.tzinfo is None:
                end_time = end_time.replace(tzinfo=timezone.utc)
            else:
                end_time = end_time.astimezone(timezone.utc)
                
            if end_time >= cutoff_date:
                recent_slices.append(s)
                
        if not recent_slices:
            return 0.0
            
        total_hours = sum(s.duration_hours for s in recent_slices)
        # Velocity is total hours completed divided by the rolling window days
        velocity = total_hours / rolling_window_days
        return round(max(0.0, velocity), 2)
