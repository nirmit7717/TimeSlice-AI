from datetime import datetime, timezone
from typing import Optional

class DeadlineRiskCalculator:
    def calculate_risk(
        self,
        remaining_effort_hours: float,
        deadline: Optional[datetime],
        velocity: float = 0.0,
        available_capacity_daily: float = 8.0
    ) -> str:
        """
        Calculates the deadline risk category: Low, Moderate, High, or Critical.
        """
        if not deadline:
            return "Low"

        # Ensure timezone-naive comparison in UTC
        if deadline.tzinfo is not None:
            deadline = deadline.astimezone(timezone.utc).replace(tzinfo=None)
        
        now = datetime.utcnow()
        time_left = deadline - now
        days_left = time_left.total_seconds() / 86400.0

        if days_left <= 0:
            return "Critical"

        if remaining_effort_hours <= 0:
            return "Low"

        # Calculate required daily hours to meet deadline
        required_daily_hours = remaining_effort_hours / days_left

        if required_daily_hours > available_capacity_daily:
            return "Critical"
        elif required_daily_hours > (available_capacity_daily * 0.75):
            return "High"
        elif velocity > 0 and required_daily_hours > velocity:
            return "Moderate"
        elif required_daily_hours > 2.0:
            return "Moderate"
        
        return "Low"
