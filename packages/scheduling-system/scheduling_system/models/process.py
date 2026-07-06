from datetime import datetime
from enum import Enum
from typing import List
from pydantic import BaseModel, Field

class ProcessLifecycle(str, Enum):
    CREATED = "Created"
    ACTIVE = "Active"
    PAUSED = "Paused"
    COMPLETED = "Completed"
    ARCHIVED = "Archived"

class Process(BaseModel):
    id: str = Field(..., description="Unique identifier for the process")
    name: str = Field(..., description="Name of the project/process")
    description: str = Field("", description="Detailed description of what the process involves")
    goal: str = Field("", description="The ultimate target or objective of this process")
    priority: int = Field(1, ge=1, le=5, description="Priority level from 1 (lowest) to 5 (highest)")
    deadline: datetime = Field(..., description="The target completion datetime")
    estimated_effort_hours: float = Field(..., gt=0, description="Estimated total hours to complete this process")
    remaining_effort_hours: float = Field(..., ge=0, description="Remaining hours to complete this process")
    status: ProcessLifecycle = Field(ProcessLifecycle.CREATED, description="Current lifecycle state of the process")
    tags: List[str] = Field(default_factory=list, description="Descriptive labels for categorizing processes")
    dependency_ids: List[str] = Field(default_factory=list, description="List of process IDs that this process depends on")
    progress: float = Field(0.0, ge=0.0, le=1.0, description="Progress ratio from 0.0 (0%) to 1.0 (100%)")
    health_score: float = Field(100.0, ge=0.0, le=100.0, description="Computed process health from 0 to 100")
    attention_debt: float = Field(0.0, ge=0.0, description="Accumulated neglect metric in hours")
    attention_equity: float = Field(0.0, ge=0.0, description="Productive momentum score")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Record creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Record last-updated timestamp")
