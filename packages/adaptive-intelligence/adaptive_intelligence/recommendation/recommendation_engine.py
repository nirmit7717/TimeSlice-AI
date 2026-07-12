"""Recommendation Engine — generates typed scheduling recommendations.

Combines the AdaptiveProfile and BanditEngine to produce a personalised
RecommendationPackage: the optimal policy + quantum for the operator's
current behavioral context.
"""

from datetime import datetime
from typing import Optional

from adaptive_intelligence.models import RecommendationPackage
from adaptive_intelligence.operator_model.operator_model import OperatorModelService
from adaptive_intelligence.adaptive_profile.adaptive_profile import AdaptiveProfileService


_POLICY_REASONS = {
    "round_robin": "Your consistent work patterns suit balanced alternation across all processes.",
    "priority": "Your high consistency score makes priority-first scheduling effective for you.",
    "sjf": "Your strong velocity suggests shortest-job-first maximises your daily output.",
    "edf": "Deadline pressure detected — earliest-deadline-first protects your commitments.",
}

_QUANTUM_REASONS = {
    0.5: "Short 30-minute sprints match your pattern of frequent context switches.",
    1.0: "1-hour sessions balance depth with your preferred break frequency.",
    2.0: "2-hour deep-work blocks align with your average focus session length.",
    3.0: "Extended 3-hour sessions suit your high consistency and low switch tolerance.",
    4.0: "4-hour marathon sessions fit your maximum-focus profile.",
}


class RecommendationEngine:
    """
    Queries the bandit and profile to assemble a RecommendationPackage.
    Requires a live DB session.
    """

    def __init__(self, db_session):
        self.db = db_session
        self._operator_svc = OperatorModelService(db_session)
        self._profile_svc = AdaptiveProfileService(db_session)

    def get_recommendation(
        self,
        operator_id: str = "default_operator",
        timestamp: Optional[datetime] = None,
    ) -> RecommendationPackage:
        """
        Runs the bandit's arm selection on the current operator context and
        returns a fully typed RecommendationPackage.

        Args:
            operator_id: The operator identifier.
            timestamp: Optional override for time-of-day features.

        Returns:
            RecommendationPackage with policy, quantum, confidence, and reason.
        """
        ts = timestamp or datetime.utcnow()

        # Load context
        context = self._operator_svc.to_context_vector_dict(operator_id)

        # Load and query bandit
        bandit = self._profile_svc.load_bandit(operator_id)
        arm_idx = bandit.select_arm(context, ts)
        policy, quantum = bandit.get_policy_quantum(arm_idx)
        confidence = bandit.get_confidence(arm_idx, context, ts)

        # Load profile for working hours
        profile = self._profile_svc.get_or_create(operator_id)

        # Build human-readable reason
        policy_reason = _POLICY_REASONS.get(policy, "Based on your scheduling history.")
        # Snap quantum reason to nearest key
        from adaptive_intelligence.contextual_bandits.bandit_engine import QUANTUMS
        nearest_q = min(QUANTUMS, key=lambda q: abs(q - quantum))
        quantum_reason = _QUANTUM_REASONS.get(nearest_q, f"{quantum}h sessions recommended.")
        reason = f"{policy_reason} {quantum_reason}"

        return RecommendationPackage(
            operator_id=operator_id,
            recommended_policy=policy,
            recommended_quantum_hours=quantum,
            preferred_work_start=profile.working_hours_start,
            preferred_work_end=profile.working_hours_end,
            confidence=confidence,
            reason=reason,
            generated_at=ts,
        )
