"""Adaptive Intelligence package for TimeSlice AI.

Provides a Contextual Bandit (LinUCB) learning engine that personalizes
scheduling policies and time quantum recommendations based on operator
behavioral data.
"""

from adaptive_intelligence.models import (
    LearningEvent,
    LearningEventType,
    RecommendationPackage,
    OperatorModelData,
    AdaptiveProfileData,
)
from adaptive_intelligence.learning_pipeline.learning_pipeline import LearningPipeline
from adaptive_intelligence.recommendation.recommendation_engine import RecommendationEngine

__all__ = [
    "LearningEvent",
    "LearningEventType",
    "RecommendationPackage",
    "OperatorModelData",
    "AdaptiveProfileData",
    "LearningPipeline",
    "RecommendationEngine",
]
