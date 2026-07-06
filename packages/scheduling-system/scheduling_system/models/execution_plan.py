from datetime import datetime
from typing import List
from pydantic import BaseModel, Field
from scheduling_system.models.time_slice import TimeSlice

class ExecutionWindow(BaseModel):
    id: str = Field(..., description="Unique identifier for the execution window")
    time_slice: TimeSlice = Field(..., description="The time slice assigned to this window")
    status: str = Field("Scheduled", description="Status of the window (e.g. Scheduled, Dynamic, Validated)")

class ExecutionPlan(BaseModel):
    id: str = Field(..., description="Unique identifier for this scheduling execution plan")
    policy_name: str = Field(..., description="The name of the scheduling policy used to generate the plan")
    time_quantum_hours: float = Field(..., gt=0, description="The time quantum/slice configuration used in hours")
    execution_windows: List[ExecutionWindow] = Field(default_factory=list, description="Ordered scheduled time blocks")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp of this execution plan")
