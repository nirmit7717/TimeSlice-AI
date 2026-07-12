"""Composite Reward Engine for Adaptive Intelligence.

Translates raw behavioral events into scalar reward signals per PRD §15.23.

Reward table:
  session_completed        → +0.8
  process_completed        → +2.0
  recommendation_accepted  → +1.0
  session_abandoned        → -1.0
  recommendation_rejected  → -0.3  (soft penalty — user still deciding)
  deadline_missed          → -2.0
"""

from adaptive_intelligence.models import LearningEvent, LearningEventType


# PRD §15.23 reward schedule
_REWARD_TABLE: dict[LearningEventType, float] = {
    LearningEventType.SESSION_COMPLETED: 0.8,
    LearningEventType.PROCESS_COMPLETED: 2.0,
    LearningEventType.RECOMMENDATION_ACCEPTED: 1.0,
    LearningEventType.SESSION_ABANDONED: -1.0,
    LearningEventType.RECOMMENDATION_REJECTED: -0.3,
    LearningEventType.DEADLINE_MISSED: -2.0,
}


class RewardEngine:
    """
    Stateless reward calculator. Given a LearningEvent, returns the
    scalar reward signal to feed into the contextual bandit update step.
    """

    def compute(self, event: LearningEvent) -> float:
        """
        Returns the base reward for an event, optionally modulated by
        contextual metadata (e.g., extra bonus if completion rate is climbing).

        Args:
            event: The LearningEvent observation.

        Returns:
            float: Signed scalar reward.
        """
        base_reward = _REWARD_TABLE.get(event.event_type, 0.0)

        # Contextual modulations — scale reward if operator consistency is high
        consistency = event.context_features.get("consistency_score", 0.5)

        if event.event_type == LearningEventType.SESSION_COMPLETED:
            # Bonus for high-consistency operators completing sessions
            if consistency > 0.75:
                base_reward += 0.2

        elif event.event_type == LearningEventType.SESSION_ABANDONED:
            # Soften penalty if operator consistency is low (still learning)
            if consistency < 0.25:
                base_reward += 0.3   # less negative

        return round(base_reward, 4)

    def get_reward_table(self) -> dict:
        """Returns the canonical reward table for inspection."""
        return {k.value: v for k, v in _REWARD_TABLE.items()}
