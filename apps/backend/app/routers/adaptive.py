"""Adaptive Intelligence API Router.

Provides endpoints for reading and overriding the operator's learned
scheduling preferences and behavioral model.

Endpoints:
  GET  /api/v1/adaptive/profile          → operator's learned preferences
  PUT  /api/v1/adaptive/profile          → manual override of preferences
  GET  /api/v1/adaptive/operator-model   → behavioral model statistics
  GET  /api/v1/adaptive/recommendation   → policy + quantum recommendation
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.connection import get_db
from adaptive_intelligence.adaptive_profile.adaptive_profile import AdaptiveProfileService
from adaptive_intelligence.operator_model.operator_model import OperatorModelService
from adaptive_intelligence.recommendation.recommendation_engine import RecommendationEngine
from adaptive_intelligence.models import AdaptiveProfileData, OperatorModelData, RecommendationPackage

router = APIRouter(tags=["adaptive"])

DEFAULT_OPERATOR = "default_operator"


# ── Request schemas ────────────────────────────────────────────────────────────

class ProfileOverrideRequest(BaseModel):
    preferred_policy: Optional[str] = None
    preferred_quantum_hours: Optional[float] = None
    working_hours_start: Optional[int] = None
    working_hours_end: Optional[int] = None
    max_daily_hours: Optional[float] = None
    telegram_chat_id: Optional[str] = None
    telegram_connected: Optional[bool] = None
    local_notifications: Optional[bool] = None


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.get("/profile", response_model=AdaptiveProfileData)
def get_adaptive_profile(db: Session = Depends(get_db)):
    """
    Returns the operator's learned adaptive profile:
    preferred scheduling policy, time quantum, working hours, and bandit confidence weights.
    """
    svc = AdaptiveProfileService(db)
    return svc.get_profile_data(DEFAULT_OPERATOR)


@router.put("/profile", response_model=AdaptiveProfileData)
def override_adaptive_profile(
    body: ProfileOverrideRequest,
    db: Session = Depends(get_db),
):
    """
    Manually override one or more learned preferences.
    Only provided (non-null) fields are updated; others remain at learned values.
    """
    svc = AdaptiveProfileService(db)
    return svc.override_profile(
        operator_id=DEFAULT_OPERATOR,
        preferred_policy=body.preferred_policy,
        preferred_quantum_hours=body.preferred_quantum_hours,
        working_hours_start=body.working_hours_start,
        working_hours_end=body.working_hours_end,
        max_daily_hours=body.max_daily_hours,
        telegram_chat_id=body.telegram_chat_id,
        telegram_connected=body.telegram_connected,
        local_notifications=body.local_notifications,
    )


@router.get("/operator-model", response_model=OperatorModelData)
def get_operator_model(db: Session = Depends(get_db)):
    """
    Returns the learned behavioral model: focus duration average,
    switch tolerance, consistency score, velocity, and session counts.
    """
    svc = OperatorModelService(db)
    return svc.get_model_data(DEFAULT_OPERATOR)


@router.get("/recommendation", response_model=RecommendationPackage)
def get_recommendation(db: Session = Depends(get_db)):
    """
    Runs the contextual bandit on the operator's current behavioral context
    and returns a personalised scheduling recommendation with reasoning.
    """
    engine = RecommendationEngine(db)
    return engine.get_recommendation(operator_id=DEFAULT_OPERATOR)
