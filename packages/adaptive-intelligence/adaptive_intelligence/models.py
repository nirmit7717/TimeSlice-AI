"""Pydantic domain models for Adaptive Intelligence Layer.

PRD §8.4, §15.21–15.25
"""
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class LearningEventType(str, Enum):
    """All observable operator events that feed the reward signal."""
    SESSION_COMPLETED = "session_completed"
    SESSION_ABANDONED = "session_abandoned"
    PROCESS_COMPLETED = "process_completed"
    RECOMMENDATION_ACCEPTED = "recommendation_accepted"
    RECOMMENDATION_REJECTED = "recommendation_rejected"
    DEADLINE_MISSED = "deadline_missed"


class LearningEvent(BaseModel):
    """A single behavioral observation emitted by the execution or kernel layer."""
    operator_id: str = Field(default="default_operator", description="Operator/user ID")
    event_type: LearningEventType
    process_id: Optional[str] = None
    slice_id: Optional[str] = None
    # Context features snapshot at the time of event
    context_features: Dict[str, Any] = Field(
        default_factory=dict,
        description="Operator model feature snapshot: focus_duration_avg, switch_tolerance, etc."
    )
    # The arm (policy + quantum combo) that was active when this event happened
    active_policy: Optional[str] = None
    active_quantum_hours: Optional[float] = None
    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RecommendationPackage(BaseModel):
    """Typed output from the Recommendation Engine."""
    operator_id: str
    recommended_policy: str = Field(
        description="One of: round_robin, priority, sjf, edf"
    )
    recommended_quantum_hours: float = Field(
        description="Recommended focus session duration in hours"
    )
    preferred_work_start: int = Field(
        default=9,
        description="Recommended work start hour (0–23)"
    )
    preferred_work_end: int = Field(
        default=21,
        description="Recommended work end hour (0–23)"
    )
    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Bandit confidence score for this arm selection"
    )
    reason: str = Field(
        default="Based on your scheduling history and behavioral patterns.",
        description="Human-readable explanation of the recommendation"
    )
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class OperatorModelData(BaseModel):
    """Snapshot of the learned operator behavioral model."""
    operator_id: str
    focus_duration_avg: float = 2.0        # Average session hours
    switch_tolerance: float = 0.5          # 0–1: low = prefers single-task
    consistency_score: float = 0.5         # 0–1: regularity of work pattern
    velocity_score: float = 0.0            # Completed hours per day
    total_slices_completed: int = 0
    total_slices_abandoned: int = 0
    completion_rate: float = 0.0           # Derived: completed / (completed + abandoned)


class AdaptiveProfileData(BaseModel):
    """Snapshot of the operator's learned preferences."""
    operator_id: str
    preferred_policy: str = "round_robin"
    preferred_quantum_hours: float = 2.0
    working_hours_start: int = 9
    working_hours_end: int = 21
    max_daily_hours: float = 8.0
    telegram_chat_id: Optional[str] = None
    telegram_connected: bool = False
    local_notifications: bool = True
    bandit_weights: Optional[Dict[str, Any]] = None   # Serialized bandit state
    last_updated: Optional[datetime] = None

