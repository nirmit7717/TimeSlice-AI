from datetime import datetime, timezone
from typing import Optional
from scheduling_system.models.process import Process

class AttentionDebtCalculator:
    def calculate_debt(self, process: Process, last_slice_date: Optional[datetime], default_neglect_days: float = 14.0) -> float:
        """
        Calculates the Attention Debt score for a process.
        Debt accumulates the longer a process goes without focused sessions, scaled by priority.
        """
        if last_slice_date is None:
            days_neglected = default_neglect_days
        else:
            if last_slice_date.tzinfo is None:
                last_slice_date = last_slice_date.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            days_neglected = max(0.0, (now - last_slice_date).total_seconds() / 86400.0)

        # Debt scaling formula
        # Base neglect * Priority factor * remaining ratio
        priority_weight = process.priority / 3.0
        remaining_ratio = process.remaining_effort_hours / max(1.0, process.estimated_effort_hours)
        
        debt = days_neglected * priority_weight * remaining_ratio
        
        return round(max(0.0, debt), 2)
