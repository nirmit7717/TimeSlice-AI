"""Adaptive Profile Manager.

Manages each operator's DbAdaptiveProfile: their learned policy preference,
quantum preference, and working hours. Bandit state is persisted as a JSON
string in the notification_prefs column (re-purposed as generic config blob)
until a dedicated column is added.

Uses a dedicated `bandit_state` JSON field strategy via the notification_prefs
fallback to avoid a new migration for now.
"""

import json
import uuid
from datetime import datetime
from typing import Optional

from adaptive_intelligence.models import AdaptiveProfileData
from adaptive_intelligence.contextual_bandits.bandit_engine import BanditEngine


class AdaptiveProfileService:
    """
    Manages DbAdaptiveProfile creation, retrieval, and updates.
    """

    BANDIT_STATE_KEY = "__bandit_state__"

    def __init__(self, db_session):
        self.db = db_session

    def get_or_create(self, operator_id: str):
        """Gets or initialises a DbAdaptiveProfile for the operator."""
        from database.models import DbAdaptiveProfile
        profile = self.db.query(DbAdaptiveProfile).filter(
            DbAdaptiveProfile.operator_id == operator_id
        ).first()
        if not profile:
            profile = DbAdaptiveProfile(
                id=str(uuid.uuid4()),
                operator_id=operator_id,
            )
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
        return profile

    def load_bandit(self, operator_id: str) -> BanditEngine:
        """
        Loads the persisted BanditEngine from the profile's notification_prefs JSON.
        Returns a fresh bandit if no state exists yet.
        """
        profile = self.get_or_create(operator_id)
        try:
            prefs = json.loads(profile.notification_prefs or "{}")
            bandit_state_json = prefs.get(self.BANDIT_STATE_KEY)
            if bandit_state_json:
                return BanditEngine.from_state_dict(bandit_state_json)
        except Exception:
            pass
        return BanditEngine()

    def save_bandit(self, operator_id: str, bandit: BanditEngine) -> None:
        """Persists bandit state back into the profile row."""
        from database.models import DbAdaptiveProfile
        profile = self.get_or_create(operator_id)
        try:
            prefs = json.loads(profile.notification_prefs or "{}")
        except Exception:
            prefs = {}
        prefs[self.BANDIT_STATE_KEY] = bandit.to_state_dict()
        profile.notification_prefs = json.dumps(prefs)
        profile.updated_at = datetime.utcnow()
        self.db.commit()

    def update_from_bandit(
        self,
        operator_id: str,
        recommended_policy: str,
        recommended_quantum_hours: float,
        bandit: BanditEngine,
    ) -> None:
        """
        Updates the profile's preferred_policy and preferred_quantum_hours
        after a bandit recommendation. Does NOT re-save bandit state here —
        caller should call save_bandit() first if needed.
        """
        from database.models import DbAdaptiveProfile
        profile = self.get_or_create(operator_id)
        profile.preferred_policy = recommended_policy
        profile.preferred_quantum_hours = recommended_quantum_hours
        profile.updated_at = datetime.utcnow()
        self.db.commit()

    def get_profile_data(self, operator_id: str) -> AdaptiveProfileData:
        """Returns a Pydantic snapshot of the adaptive profile."""
        profile = self.get_or_create(operator_id)
        try:
            prefs = json.loads(profile.notification_prefs or "{}")
            bandit_raw = prefs.get(self.BANDIT_STATE_KEY)
            bandit_weights = json.loads(bandit_raw) if bandit_raw else None
            telegram_chat_id = prefs.get("telegram_chat_id")
            telegram_connected = prefs.get("telegram_connected", False)
            local_notifications = prefs.get("local_notifications", True)
        except Exception:
            bandit_weights = None
            telegram_chat_id = None
            telegram_connected = False
            local_notifications = True

        return AdaptiveProfileData(
            operator_id=profile.operator_id,
            preferred_policy=profile.preferred_policy,
            preferred_quantum_hours=profile.preferred_quantum_hours,
            working_hours_start=profile.working_hours_start,
            working_hours_end=profile.working_hours_end,
            max_daily_hours=profile.max_daily_hours,
            telegram_chat_id=telegram_chat_id,
            telegram_connected=telegram_connected,
            local_notifications=local_notifications,
            bandit_weights=bandit_weights,
            last_updated=profile.updated_at,
        )

    def override_profile(
        self,
        operator_id: str,
        preferred_policy: Optional[str] = None,
        preferred_quantum_hours: Optional[float] = None,
        working_hours_start: Optional[int] = None,
        working_hours_end: Optional[int] = None,
        max_daily_hours: Optional[float] = None,
        telegram_chat_id: Optional[str] = None,
        telegram_connected: Optional[bool] = None,
        local_notifications: Optional[bool] = None,
    ) -> AdaptiveProfileData:
        """
        Allows the operator to manually override learned preferences.
        Only provided (non-None) fields are updated.
        """
        profile = self.get_or_create(operator_id)
        if preferred_policy is not None:
            profile.preferred_policy = preferred_policy
        if preferred_quantum_hours is not None:
            profile.preferred_quantum_hours = preferred_quantum_hours
        if working_hours_start is not None:
            profile.working_hours_start = working_hours_start
        if working_hours_end is not None:
            profile.working_hours_end = working_hours_end
        if max_daily_hours is not None:
            profile.max_daily_hours = max_daily_hours

        # Update notification_prefs JSON string field
        try:
            prefs = json.loads(profile.notification_prefs or "{}")
        except Exception:
            prefs = {}

        if telegram_chat_id is not None:
            prefs["telegram_chat_id"] = telegram_chat_id
        if telegram_connected is not None:
            prefs["telegram_connected"] = telegram_connected
        if local_notifications is not None:
            prefs["local_notifications"] = local_notifications

        profile.notification_prefs = json.dumps(prefs)
        profile.updated_at = datetime.utcnow()
        self.db.commit()
        return self.get_profile_data(operator_id)

