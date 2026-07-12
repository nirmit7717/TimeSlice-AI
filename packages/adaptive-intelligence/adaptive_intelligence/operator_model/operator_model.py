"""Operator Model — tracks and updates the learned behavioral model.

The operator model captures rolling statistics of how an operator works:
  - Average focus session duration
  - Switch tolerance (preference for single-tasking vs. multi-tasking)
  - Consistency score (regularity of daily work patterns)
  - Velocity score (completed effort hours per day)

These features form the context vector fed into the LinUCB bandit.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional

from adaptive_intelligence.models import LearningEvent, LearningEventType, OperatorModelData


class OperatorModelService:
    """
    Updates and retrieves the operator behavioral model from the database.
    Designed to work directly with an SQLAlchemy DB session.
    """

    def __init__(self, db_session):
        self.db = db_session

    def get_or_create(self, operator_id: str):
        """
        Fetches or initialises a DbOperatorModel row for the operator.
        """
        from database.models import DbOperatorModel
        model = self.db.query(DbOperatorModel).filter(
            DbOperatorModel.operator_id == operator_id
        ).first()
        if not model:
            model = DbOperatorModel(
                id=str(uuid.uuid4()),
                operator_id=operator_id,
            )
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
        return model

    def update_from_event(self, event: LearningEvent) -> None:
        """
        Updates the operator model based on a behavioral event.

        Updates applied:
          - SESSION_COMPLETED: increment completed count, update velocity and consistency
          - SESSION_ABANDONED: increment abandoned count
          - PROCESS_COMPLETED: no direct model update (reward-only event)
        """
        from database.models import DbOperatorModel, DbTimeSlice
        model = self.get_or_create(event.operator_id)

        if event.event_type == LearningEventType.SESSION_COMPLETED:
            model.total_slices_completed += 1

            # Update rolling focus duration average
            old_avg = model.focus_duration_avg
            count = model.total_slices_completed
            # Rolling mean: new_avg = old_avg + (new_value - old_avg) / count
            session_hours = event.context_features.get("duration_hours", old_avg)
            model.focus_duration_avg = old_avg + (session_hours - old_avg) / count

            # Update velocity score: compute hours completed in past 7 days
            try:
                cutoff = datetime.utcnow() - timedelta(days=7)
                recent_slices = (
                    self.db.query(DbTimeSlice)
                    .filter(
                        DbTimeSlice.status == "Completed",
                        DbTimeSlice.end_time >= cutoff
                    )
                    .all()
                )
                total_hours = sum(s.duration_hours for s in recent_slices)
                model.velocity_score = round(total_hours / 7.0, 3)
            except Exception:
                pass  # Non-critical; don't fail the learning pipeline

        elif event.event_type == LearningEventType.SESSION_ABANDONED:
            model.total_slices_abandoned += 1

        # Recompute consistency score: completed / (completed + abandoned)
        total_sessions = model.total_slices_completed + model.total_slices_abandoned
        if total_sessions > 0:
            model.consistency_score = round(
                model.total_slices_completed / total_sessions, 3
            )

        # Switch tolerance: derived from context_features if provided
        # (Decreases when user abandons; increases when consistent)
        if event.event_type == LearningEventType.SESSION_COMPLETED:
            model.switch_tolerance = min(1.0, model.switch_tolerance + 0.02)
        elif event.event_type == LearningEventType.SESSION_ABANDONED:
            model.switch_tolerance = max(0.0, model.switch_tolerance - 0.05)

        model.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(model)

    def get_model_data(self, operator_id: str) -> OperatorModelData:
        """Returns a Pydantic snapshot of the operator model."""
        model = self.get_or_create(operator_id)
        total = model.total_slices_completed + model.total_slices_abandoned
        completion_rate = (
            round(model.total_slices_completed / total, 3) if total > 0 else 0.0
        )
        return OperatorModelData(
            operator_id=model.operator_id,
            focus_duration_avg=model.focus_duration_avg,
            switch_tolerance=model.switch_tolerance,
            consistency_score=model.consistency_score,
            velocity_score=model.velocity_score,
            total_slices_completed=model.total_slices_completed,
            total_slices_abandoned=model.total_slices_abandoned,
            completion_rate=completion_rate,
        )

    def to_context_vector_dict(self, operator_id: str) -> dict:
        """
        Builds the context dict that feeds into the LinUCB feature vector.
        """
        model = self.get_or_create(operator_id)
        return {
            "focus_duration_avg": model.focus_duration_avg,
            "switch_tolerance": model.switch_tolerance,
            "consistency_score": model.consistency_score,
            "velocity_score": model.velocity_score,
        }
