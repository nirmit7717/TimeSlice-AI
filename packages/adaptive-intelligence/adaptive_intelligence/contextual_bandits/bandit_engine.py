"""LinUCB Contextual Bandit Engine for policy/quantum selection.

Implements a disjoint LinUCB bandit where each arm is a (policy, quantum)
combination. The bandit learns which scheduling strategy produces the highest
cumulative reward for each operator's behavioral context.

Arms (20 total):
  Policies: round_robin, priority, sjf, edf
  Quantums: 0.5h, 1h, 2h, 3h, 4h

Feature vector (6-dim):
  [focus_duration_avg, switch_tolerance, consistency_score,
   velocity_score, normalized_hour_of_day, normalized_day_of_week]

Reference: Li et al. 2010 — "A Contextual-Bandit Approach to Personalized
News Article Recommendation" (LinUCB disjoint model).
"""

import json
import math
from datetime import datetime
from typing import List, Optional, Tuple

import numpy as np


# ── Arms definition ────────────────────────────────────────────────────────────
POLICIES: List[str] = ["round_robin", "priority", "sjf", "edf"]
QUANTUMS: List[float] = [0.5, 1.0, 2.0, 3.0, 4.0]

# All arms as (policy, quantum) tuples — 20 arms total
ARMS: List[Tuple[str, float]] = [
    (policy, quantum)
    for policy in POLICIES
    for quantum in QUANTUMS
]

FEATURE_DIM: int = 6       # Dimensionality of the context feature vector
ALPHA: float = 1.0         # Exploration parameter (higher = more exploration)


def _build_feature_vector(context: dict, timestamp: Optional[datetime] = None) -> np.ndarray:
    """
    Builds a normalised 6-dimensional feature vector from operator context.

    Args:
        context: Dict of operator model fields.
        timestamp: Optional datetime for time-of-day features.

    Returns:
        np.ndarray of shape (FEATURE_DIM,)
    """
    ts = timestamp or datetime.utcnow()

    # Normalise focus_duration_avg to [0,1] assuming max 8h sessions
    focus = min(context.get("focus_duration_avg", 2.0), 8.0) / 8.0
    switch_tol = float(context.get("switch_tolerance", 0.5))
    consistency = float(context.get("consistency_score", 0.5))
    # Normalise velocity to [0,1] assuming max 12h/day
    velocity = min(context.get("velocity_score", 0.0), 12.0) / 12.0
    hour_norm = ts.hour / 23.0
    day_norm = ts.weekday() / 6.0   # Monday=0, Sunday=6

    return np.array([focus, switch_tol, consistency, velocity, hour_norm, day_norm], dtype=float)


class BanditEngine:
    """
    Disjoint LinUCB bandit engine.

    Each arm maintains its own A matrix (d×d) and b vector (d×1) for the
    linear regression model. Parameters are persisted as JSON via the
    `to_state_dict` / `from_state_dict` methods so they survive restarts.
    """

    def __init__(self, alpha: float = ALPHA):
        self.alpha = alpha
        self.n_arms = len(ARMS)
        self.d = FEATURE_DIM

        # Per-arm parameter matrices
        # A_a = (d × d) identity matrix, b_a = zero vector (d,)
        self.A: List[np.ndarray] = [np.eye(self.d) for _ in range(self.n_arms)]
        self.b: List[np.ndarray] = [np.zeros(self.d) for _ in range(self.n_arms)]

    # ── Core LinUCB methods ─────────────────────────────────────────────────────

    def select_arm(self, context: dict, timestamp: Optional[datetime] = None) -> int:
        """
        Selects the arm with the highest UCB score given the context.

        Returns:
            int: Index into ARMS list.
        """
        x = _build_feature_vector(context, timestamp)
        ucb_scores = []

        for arm_idx in range(self.n_arms):
            A_inv = np.linalg.inv(self.A[arm_idx])
            theta = A_inv @ self.b[arm_idx]
            ucb = (theta @ x) + self.alpha * math.sqrt(x @ A_inv @ x)
            ucb_scores.append(ucb)

        return int(np.argmax(ucb_scores))

    def update(self, arm_idx: int, reward: float, context: dict, timestamp: Optional[datetime] = None) -> None:
        """
        Updates the bandit matrices for the given arm using the received reward.

        Args:
            arm_idx: The arm index (from `select_arm` or derived from active policy).
            reward: The scalar reward signal from `RewardEngine`.
            context: Operator context at the time of the event.
            timestamp: Optional timestamp for time features.
        """
        x = _build_feature_vector(context, timestamp)
        self.A[arm_idx] = self.A[arm_idx] + np.outer(x, x)
        self.b[arm_idx] = self.b[arm_idx] + reward * x

    def get_policy_quantum(self, arm_idx: int) -> Tuple[str, float]:
        """Maps an arm index to its (policy, quantum_hours) tuple."""
        return ARMS[arm_idx]

    def get_confidence(self, arm_idx: int, context: dict, timestamp: Optional[datetime] = None) -> float:
        """
        Computes a normalised confidence score [0,1] for the selected arm.
        Higher means the bandit is more certain about this arm's superiority.
        """
        x = _build_feature_vector(context, timestamp)
        A_inv = np.linalg.inv(self.A[arm_idx])
        theta = A_inv @ self.b[arm_idx]
        estimated_reward = float(theta @ x)
        # Normalise: map estimated_reward from [-2, 2] range to [0, 1]
        return float(min(1.0, max(0.0, (estimated_reward + 2.0) / 4.0)))

    # ── Persistence ─────────────────────────────────────────────────────────────

    def to_state_dict(self) -> str:
        """Serialises bandit state to a JSON string for DB persistence."""
        state = {
            "alpha": self.alpha,
            "n_arms": self.n_arms,
            "d": self.d,
            "A": [a.tolist() for a in self.A],
            "b": [b.tolist() for b in self.b],
        }
        return json.dumps(state)

    @classmethod
    def from_state_dict(cls, state_json: str) -> "BanditEngine":
        """Restores a BanditEngine from a serialised JSON string."""
        state = json.loads(state_json)
        engine = cls(alpha=state["alpha"])
        engine.n_arms = state["n_arms"]
        engine.d = state["d"]
        engine.A = [np.array(a) for a in state["A"]]
        engine.b = [np.array(b) for b in state["b"]]
        return engine

    def get_arm_index_for_policy(self, policy: str, quantum_hours: float) -> int:
        """
        Looks up the arm index closest to the given policy + quantum combination.
        Falls back to the nearest quantum if exact match is not found.
        """
        # Snap quantum to the nearest discrete quantum in QUANTUMS
        nearest_quantum = min(QUANTUMS, key=lambda q: abs(q - quantum_hours))
        try:
            return ARMS.index((policy, nearest_quantum))
        except ValueError:
            return 0   # fallback to first arm
