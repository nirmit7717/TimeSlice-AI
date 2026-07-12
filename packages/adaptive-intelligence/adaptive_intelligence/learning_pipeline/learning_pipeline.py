"""Learning Pipeline — full observation → reward → bandit update loop.

Orchestrates the entire learning cycle:
  1. Receive a LearningEvent from the execution / kernel layer
  2. Enrich event context from the current OperatorModel
  3. Compute reward via RewardEngine
  4. Determine the active arm (policy + quantum in use)
  5. Update bandit weights
  6. Persist updated profile and operator model
"""

from datetime import datetime

from adaptive_intelligence.models import LearningEvent, LearningEventType
from adaptive_intelligence.reward.reward_engine import RewardEngine
from adaptive_intelligence.operator_model.operator_model import OperatorModelService
from adaptive_intelligence.adaptive_profile.adaptive_profile import AdaptiveProfileService
from adaptive_intelligence.contextual_bandits.bandit_engine import BanditEngine


class LearningPipeline:
    """
    Stateless orchestrator. Requires a live DB session on each call so it
    integrates cleanly with FastAPI's dependency injection pattern.
    """

    def __init__(self, db_session):
        self.db = db_session
        self._reward_engine = RewardEngine()
        self._operator_svc = OperatorModelService(db_session)
        self._profile_svc = AdaptiveProfileService(db_session)

    def observe(self, event: LearningEvent) -> float:
        """
        Processes one LearningEvent through the full pipeline.

        Steps:
          1. Enrich context from operator model.
          2. Compute reward.
          3. Load (or initialise) the bandit for this operator.
          4. Update bandit with the arm that was active.
          5. Persist updated bandit + profile.
          6. Update operator model stats.

        Returns:
            float: The computed reward signal (for logging / debugging).
        """
        # 1. Enrich event context
        context = self._operator_svc.to_context_vector_dict(event.operator_id)
        # Merge any caller-supplied features (e.g., duration_hours from slice)
        context.update(event.context_features)
        event.context_features = context

        # 2. Compute reward
        reward = self._reward_engine.compute(event)

        # 3. Load persisted bandit
        bandit = self._profile_svc.load_bandit(event.operator_id)

        # 4. Determine which arm was active when the event fired
        if event.active_policy and event.active_quantum_hours:
            arm_idx = bandit.get_arm_index_for_policy(
                event.active_policy, event.active_quantum_hours
            )
        else:
            # Fall back: load from profile
            profile = self._profile_svc.get_or_create(event.operator_id)
            arm_idx = bandit.get_arm_index_for_policy(
                profile.preferred_policy, profile.preferred_quantum_hours
            )

        # 5. Update bandit weights
        bandit.update(arm_idx, reward, context, event.timestamp)

        # 6. Select the new best arm and update profile preferences
        best_arm = bandit.select_arm(context, event.timestamp)
        new_policy, new_quantum = bandit.get_policy_quantum(best_arm)

        # Persist the updated bandit state first, then update profile fields
        self._profile_svc.save_bandit(event.operator_id, bandit)
        self._profile_svc.update_from_bandit(
            event.operator_id, new_policy, new_quantum, bandit
        )

        # 7. Update operator behavioral model stats
        self._operator_svc.update_from_event(event)

        return reward
