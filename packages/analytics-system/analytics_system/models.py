from datetime import datetime
from typing import List, Dict
from pydantic import BaseModel

class FocusHoursEntry(BaseModel):
    day: str
    hours: float

class TimeAllocationEntry(BaseModel):
    name: str
    hours: float

class WeeklySummary(BaseModel):
    streak_days: int
    total_hours: float
    avg_hours_per_day: float
    time_allocation: List[TimeAllocationEntry]
    weekly_focus_hours: List[FocusHoursEntry]
