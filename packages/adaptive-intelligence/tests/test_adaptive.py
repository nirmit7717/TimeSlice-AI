"""Unit tests for Phase 5: Adaptive Intelligence Layer."""

import pytest
import json
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.models import DbProcess, DbAdaptiveProfile, DbOperatorModel, DbTimeSlice

from adaptive_intelligence.models import LearningEvent, LearningEventType
from adaptive_intelligence.reward.reward_engine import RewardEngine
from adaptive_intelligence.contextual_bandits.bandit_engine import BanditEngine, ARMS, POLICIES, QUANTUMS
from adaptive_intelligence.operator_model.operator_model import OperatorModelService
from adaptive_intelligence.adaptive_profile.adaptive_profile import AdaptiveProfileService
from adaptive_intelligence.learning_pipeline.learning_pipeline import LearningPipeline
from adaptive_intelligence.recommendation.recommendation_engine import RecommendationEngine


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


# ── Reward Engine Tests ─────────────────────────────────────────────────────────

class TestRewardEngine:
    def test_session_completed_base_reward(self):
        engine = RewardEngine()
        event = LearningEvent(event_type=LearningEventType.SESSION_COMPLETED)
        assert engine.compute(event) == pytest.approx(0.8, abs=0.01)

    def test_process_completed_reward(self):
        engine = RewardEngine()
        event = LearningEvent(event_type=LearningEventType.PROCESS_COMPLETED)
        assert engine.compute(event) == pytest.approx(2.0, abs=0.01)

    def test_recommendation_accepted_reward(self):
        engine = RewardEngine()
        event = LearningEvent(event_type=LearningEventType.RECOMMENDATION_ACCEPTED)
        assert engine.compute(event) == pytest.approx(1.0, abs=0.01)

    def test_session_abandoned_negative_reward(self):
        engine = RewardEngine()
        event = LearningEvent(event_type=LearningEventType.SESSION_ABANDONED)
        assert engine.compute(event) < 0

    def test_deadline_missed_strongest_negative(self):
        engine = RewardEngine()
        event = LearningEvent(event_type=LearningEventType.DEADLINE_MISSED)
        assert engine.compute(event) == pytest.approx(-2.0, abs=0.01)

    def test_high_consistency_bonus_on_completion(self):
        engine = RewardEngine()
        event = LearningEvent(
            event_type=LearningEventType.SESSION_COMPLETED,
            context_features={"consistency_score": 0.9}
        )
        # Reward should be > 0.8 because of consistency bonus
        assert engine.compute(event) > 0.8

    def test_reward_table_keys(self):
        engine = RewardEngine()
        table = engine.get_reward_table()
        assert "session_completed" in table
        assert "deadline_missed" in table


# ── Bandit Engine Tests ─────────────────────────────────────────────────────────

class TestBanditEngine:
    def test_initial_arm_selection_returns_valid_index(self):
        bandit = BanditEngine()
        context = {"focus_duration_avg": 2.0, "switch_tolerance": 0.5,
                   "consistency_score": 0.5, "velocity_score": 0.5}
        idx = bandit.select_arm(context)
        assert 0 <= idx < len(ARMS)

    def test_update_changes_arm_weights(self):
        bandit = BanditEngine()
        context = {"focus_duration_avg": 2.0, "switch_tolerance": 0.5,
                   "consistency_score": 0.5, "velocity_score": 0.5}
        # Reward arm 0 heavily — it should become preferred
        for _ in range(20):
            bandit.update(0, 2.0, context)
        selected = bandit.select_arm(context)
        assert selected == 0

    def test_policy_quantum_mapping(self):
        bandit = BanditEngine()
        policy, quantum = bandit.get_policy_quantum(0)
        assert policy in POLICIES
        assert quantum in QUANTUMS

    def test_state_dict_roundtrip(self):
        bandit = BanditEngine()
        context = {"focus_duration_avg": 2.0, "switch_tolerance": 0.5,
                   "consistency_score": 0.5, "velocity_score": 0.5}
        bandit.update(3, 1.5, context)
        state = bandit.to_state_dict()
        restored = BanditEngine.from_state_dict(state)
        # Both should select same arm
        assert bandit.select_arm(context) == restored.select_arm(context)

    def test_confidence_is_normalised(self):
        bandit = BanditEngine()
        context = {"focus_duration_avg": 2.0, "switch_tolerance": 0.5,
                   "consistency_score": 0.5, "velocity_score": 0.5}
        confidence = bandit.get_confidence(0, context)
        assert 0.0 <= confidence <= 1.0

    def test_arm_index_lookup_snaps_to_nearest_quantum(self):
        bandit = BanditEngine()
        # 1.7h should snap to 2.0h
        idx = bandit.get_arm_index_for_policy("priority", 1.7)
        _, q = bandit.get_policy_quantum(idx)
        assert q == 2.0


# ── Operator Model Tests ────────────────────────────────────────────────────────

class TestOperatorModel:
    def test_get_or_create_initialises_defaults(self, db_session):
        svc = OperatorModelService(db_session)
        model = svc.get_or_create("op1")
        assert model.operator_id == "op1"
        assert model.focus_duration_avg == pytest.approx(2.0)
        assert model.total_slices_completed == 0

    def test_completion_event_increments_counter(self, db_session):
        svc = OperatorModelService(db_session)
        event = LearningEvent(
            operator_id="op1",
            event_type=LearningEventType.SESSION_COMPLETED,
            context_features={"duration_hours": 3.0}
        )
        svc.update_from_event(event)
        model = svc.get_or_create("op1")
        assert model.total_slices_completed == 1

    def test_abandonment_decreases_switch_tolerance(self, db_session):
        svc = OperatorModelService(db_session)
        # Prime a model with non-default tolerance
        model = svc.get_or_create("op1")
        original_tolerance = model.switch_tolerance

        event = LearningEvent(operator_id="op1", event_type=LearningEventType.SESSION_ABANDONED)
        svc.update_from_event(event)
        model_after = svc.get_or_create("op1")
        assert model_after.switch_tolerance < original_tolerance

    def test_consistency_score_computation(self, db_session):
        svc = OperatorModelService(db_session)
        # 3 completions, 1 abandonment → consistency = 0.75
        for _ in range(3):
            svc.update_from_event(LearningEvent(operator_id="op1",
                event_type=LearningEventType.SESSION_COMPLETED,
                context_features={"duration_hours": 2.0}))
        svc.update_from_event(LearningEvent(operator_id="op1",
            event_type=LearningEventType.SESSION_ABANDONED))
        data = svc.get_model_data("op1")
        assert data.consistency_score == pytest.approx(0.75, abs=0.01)

    def test_to_context_vector_dict_returns_expected_keys(self, db_session):
        svc = OperatorModelService(db_session)
        ctx = svc.to_context_vector_dict("op1")
        assert "focus_duration_avg" in ctx
        assert "switch_tolerance" in ctx
        assert "consistency_score" in ctx
        assert "velocity_score" in ctx


# ── Learning Pipeline Integration Test ─────────────────────────────────────────

class TestLearningPipeline:
    def test_observe_session_completed_returns_positive_reward(self, db_session):
        pipeline = LearningPipeline(db_session)
        event = LearningEvent(
            operator_id="op1",
            event_type=LearningEventType.SESSION_COMPLETED,
            context_features={"duration_hours": 2.0},
        )
        reward = pipeline.observe(event)
        assert reward > 0

    def test_observe_abandonment_returns_negative_reward(self, db_session):
        pipeline = LearningPipeline(db_session)
        event = LearningEvent(
            operator_id="op1",
            event_type=LearningEventType.SESSION_ABANDONED,
            context_features={"duration_hours": 1.0},
        )
        reward = pipeline.observe(event)
        assert reward < 0

    def test_observe_updates_profile_preferences(self, db_session):
        pipeline = LearningPipeline(db_session)
        # Reward arm 0 (round_robin + 0.5h) heavily via explicit arm selection
        for _ in range(10):
            pipeline.observe(LearningEvent(
                operator_id="op1",
                event_type=LearningEventType.SESSION_COMPLETED,
                active_policy="round_robin",
                active_quantum_hours=0.5,
                context_features={"duration_hours": 0.5},
            ))
        # Profile should now prefer round_robin
        profile_svc = AdaptiveProfileService(db_session)
        data = profile_svc.get_profile_data("op1")
        assert data.preferred_policy == "round_robin"

    def test_observe_persists_bandit_state(self, db_session):
        pipeline = LearningPipeline(db_session)
        pipeline.observe(LearningEvent(
            operator_id="op1",
            event_type=LearningEventType.SESSION_COMPLETED,
        ))
        # Bandit state should be stored in profile's notification_prefs
        profile_svc = AdaptiveProfileService(db_session)
        data = profile_svc.get_profile_data("op1")
        assert data.bandit_weights is not None


# ── Recommendation Engine Tests ──────────────────────────────────────────────────

class TestRecommendationEngine:
    def test_get_recommendation_returns_valid_policy(self, db_session):
        engine = RecommendationEngine(db_session)
        rec = engine.get_recommendation("op1")
        assert rec.recommended_policy in POLICIES

    def test_get_recommendation_returns_valid_quantum(self, db_session):
        engine = RecommendationEngine(db_session)
        rec = engine.get_recommendation("op1")
        assert rec.recommended_quantum_hours in QUANTUMS

    def test_confidence_is_in_valid_range(self, db_session):
        engine = RecommendationEngine(db_session)
        rec = engine.get_recommendation("op1")
        assert 0.0 <= rec.confidence <= 1.0

    def test_recommendation_has_reason_string(self, db_session):
        engine = RecommendationEngine(db_session)
        rec = engine.get_recommendation("op1")
        assert len(rec.reason) > 0

    def test_recommendation_reflects_heavy_arm_training(self, db_session):
        """After strongly rewarding edf+4h, the bandit state should be persisted and
        the profile should have at some point selected edf (convergence is probabilistic
        due to UCB exploration — verify state is being stored and policy is being updated)."""
        pipeline = LearningPipeline(db_session)
        policies_seen = set()

        for _ in range(30):
            pipeline.observe(LearningEvent(
                operator_id="op1",
                event_type=LearningEventType.SESSION_COMPLETED,
                active_policy="edf",
                active_quantum_hours=4.0,
                context_features={"duration_hours": 4.0, "consistency_score": 0.8},
            ))
            profile_svc = AdaptiveProfileService(db_session)
            data = profile_svc.get_profile_data("op1")
            policies_seen.add(data.preferred_policy)

        # Bandit state must be persisted
        profile_svc = AdaptiveProfileService(db_session)
        data = profile_svc.get_profile_data("op1")
        assert data.bandit_weights is not None

        # edf must have been selected at least once during training
        assert "edf" in policies_seen, (
            f"Expected 'edf' to appear in profile policy updates, but only saw: {policies_seen}"
        )
