from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

class CamelModel(BaseModel):
    """Base class configuration translating snake_case variables to camelCase JSON API schemas."""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )

class ProcessCreate(CamelModel):
    name: str
    description: Optional[str] = ""
    goal: Optional[str] = ""
    priority: Optional[int] = 1
    deadline: datetime
    estimated_effort_hours: float
    remaining_effort_hours: Optional[float] = None
    status: Optional[str] = "Active"
    tags: Optional[List[str]] = None
    dependency_ids: Optional[List[str]] = None

class ProcessUpdate(CamelModel):
    name: Optional[str] = None
    description: Optional[str] = None
    goal: Optional[str] = None
    priority: Optional[int] = None
    deadline: Optional[datetime] = None
    estimated_effort_hours: Optional[float] = None
    remaining_effort_hours: Optional[float] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    dependency_ids: Optional[List[str]] = None
    progress: Optional[float] = None
    health_score: Optional[float] = None
    attention_debt: Optional[float] = None
    attention_equity: Optional[float] = None

class ProcessResponse(CamelModel):
    id: str
    name: str
    description: str
    goal: str
    priority: int
    deadline: datetime
    estimated_effort_hours: float
    remaining_effort_hours: float
    status: str
    tags: List[str]
    dependency_ids: List[str]
    progress: float
    health_score: float
    attention_debt: float
    attention_equity: float
    created_at: datetime
    updated_at: datetime

class TimeSliceCreate(CamelModel):
    process_id: str
    start_time: datetime
    end_time: datetime
    duration_hours: float
    status: Optional[str] = "Scheduled"
    reflection: Optional[str] = None
    progress_gained: Optional[float] = 0.0

class TimeSliceResponse(CamelModel):
    id: str
    process_id: str
    start_time: datetime
    end_time: datetime
    duration_hours: float
    status: str
    reflection: Optional[str] = None
    progress_gained: float

class ExecutionWindowResponse(CamelModel):
    id: str
    time_slice: TimeSliceResponse

class ExecutionPlanResponse(CamelModel):
    id: str
    policy_name: str
    time_quantum_hours: float
    execution_windows: List[ExecutionWindowResponse]
    created_at: datetime

class RescheduleRequest(CamelModel):
    event_type: str
    start_time: datetime
    end_time: datetime

class SimulationRequest(CamelModel):
    policy_name: str
    available_hours: Optional[float] = 24.0
    quantum_hours: Optional[float] = 2.0

class SimulationResponse(CamelModel):
    policy_name: str
    is_feasible: bool
    total_slices: int
    total_scheduled_hours: float
    context_switches: int
    neglected_processes_count: int
    neglected_process_ids: List[str]
    deadline_misses_count: int
    deadline_miss_ids: List[str]

class VectorQueryRequest(CamelModel):
    query_text: str
    n_results: Optional[int] = 3

class VectorDocumentAdd(CamelModel):
    doc_id: str
    text: str
    metadata: Optional[Dict[str, Any]] = None


class PlanRequest(CamelModel):
    policy_name: str
    available_hours: Optional[float] = 24.0
    quantum_hours: Optional[float] = 2.0
    blocked_intervals: Optional[List[List[datetime]]] = None


class RecommendationResponse(CamelModel):
    process_name: str
    process_id: str
    policy_name: str
    duration_hours: float
    deadline: Optional[datetime] = None
    priority: int
    attention_debt: float
    confidence_score: float
    reasons: List[str]


class AnalyticsMetricsResponse(CamelModel):
    process_id: str
    attention_debt: float
    attention_equity: float
    deadline_risk: str
    completion_velocity: float
    process_health: float
    health_status: str
    last_computed_at: datetime


class FocusHoursEntrySchema(CamelModel):
    day: str
    hours: float


class TimeAllocationEntrySchema(CamelModel):
    name: str
    hours: float


class WeeklySummaryResponse(CamelModel):
    streak_days: int
    total_hours: float
    avg_hours_per_day: float
    time_allocation: List[TimeAllocationEntrySchema]
    weekly_focus_hours: List[FocusHoursEntrySchema]


class StartSliceRequest(CamelModel):
    process_id: str
    duration_hours: Optional[float] = 2.0


class CompleteSliceRequest(CamelModel):
    progress_gained: float
    reflection: str


class AbandonSliceRequest(CamelModel):
    reflection: str


class ChecklistItemResponse(CamelModel):
    id: str
    time_slice_id: str
    title: str
    completed: bool
    order: int


class CreateChecklistItemRequest(CamelModel):
    title: str
    order: Optional[int] = 0




