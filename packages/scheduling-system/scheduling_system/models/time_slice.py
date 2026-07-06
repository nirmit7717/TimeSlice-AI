from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class SliceStatus(str, Enum):
    SCHEDULED = "Scheduled"
    COMPLETED = "Completed"
    MISSED = "Missed"
    RESCHEDULED = "Rescheduled"

class TimeSlice(BaseModel):
    id: str = Field(..., description="Unique identifier for the scheduled time slice")
    process_id: str = Field(..., description="The ID of the process associated with this time slice")
    start_time: datetime = Field(..., description="Work session start time")
    end_time: datetime = Field(..., description="Work session end time")
    duration_hours: float = Field(..., gt=0, description="Duration in decimal hours")
    status: SliceStatus = Field(SliceStatus.SCHEDULED, description="Execution status of this slice")
    reflection: Optional[str] = Field(None, description="Operator's qualitative reflection/feedback post-execution")
    progress_gained: float = Field(0.0, ge=0.0, description="Estimated process progress percentage increment achieved")
