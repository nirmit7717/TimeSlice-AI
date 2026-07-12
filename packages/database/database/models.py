import json
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, TypeDecorator, Boolean, Text
from sqlalchemy.orm import relationship
from database.connection import Base

class JSONEncodedList(TypeDecorator):
    """Allows storing string lists as JSON arrays in SQLite text columns."""
    impl = String

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return "[]"

    def process_result_value(self, value, dialect):
        if value is not None:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return []
        return []

class DbProcess(Base):
    __tablename__ = "processes"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, default="")
    goal = Column(String, default="")
    priority = Column(Integer, default=1)
    deadline = Column(DateTime, nullable=False)
    estimated_effort_hours = Column(Float, nullable=False)
    remaining_effort_hours = Column(Float, nullable=False)
    status = Column(String, default="Created")
    tags = Column(JSONEncodedList, default=list)
    dependency_ids = Column(JSONEncodedList, default=list)
    progress = Column(Float, default=0.0)
    health_score = Column(Float, default=100.0)
    attention_debt = Column(Float, default=0.0)
    attention_equity = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    time_slices = relationship("DbTimeSlice", back_populates="process", cascade="all, delete-orphan")
    analytics = relationship("DbAnalytics", back_populates="process", uselist=False, cascade="all, delete-orphan")

class DbTimeSlice(Base):
    __tablename__ = "time_slices"

    id = Column(String, primary_key=True, index=True)
    process_id = Column(String, ForeignKey("processes.id", ondelete="CASCADE"), nullable=False, index=True)
    execution_plan_id = Column(String, nullable=True)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    duration_hours = Column(Float, nullable=False)
    status = Column(String, default="Scheduled")
    reflection = Column(Text, nullable=True)
    progress_gained = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    process = relationship("DbProcess", back_populates="time_slices")
    checklists = relationship("DbChecklist", back_populates="time_slice", cascade="all, delete-orphan")


class DbChecklist(Base):
    """Process Checklist items for a Time Slice session. PRD §17.4"""
    __tablename__ = "checklists"

    id = Column(String, primary_key=True, index=True)
    time_slice_id = Column(String, ForeignKey("time_slices.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    time_slice = relationship("DbTimeSlice", back_populates="checklists")


class DbAnalytics(Base):
    """Per-process analytics metrics. PRD §17.4"""
    __tablename__ = "analytics"

    id = Column(String, primary_key=True, index=True)
    process_id = Column(String, ForeignKey("processes.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    attention_debt = Column(Float, default=0.0)
    attention_equity = Column(Float, default=0.0)
    deadline_risk = Column(String, default="Low")          # Low | Moderate | High | Critical
    completion_velocity = Column(Float, default=0.0)        # hours/day
    process_health = Column(Float, default=100.0)
    health_status = Column(String, default="Excellent")     # Excellent | Good | Fair | Needs Attention | Critical
    last_computed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    process = relationship("DbProcess", back_populates="analytics")


class DbAdaptiveProfile(Base):
    """Operator's learned preferences. PRD §17.4"""
    __tablename__ = "adaptive_profiles"

    id = Column(String, primary_key=True, index=True)
    operator_id = Column(String, nullable=False, unique=True, index=True)
    preferred_policy = Column(String, default="round_robin")
    preferred_quantum_hours = Column(Float, default=2.0)
    working_hours_start = Column(Integer, default=9)        # Hour of day (0-23)
    working_hours_end = Column(Integer, default=21)
    max_daily_hours = Column(Float, default=8.0)
    notification_prefs = Column(String, default="{}")       # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DbOperatorModel(Base):
    """Learned behavioral model of the Operator. PRD §17.4"""
    __tablename__ = "operator_models"

    id = Column(String, primary_key=True, index=True)
    operator_id = Column(String, nullable=False, unique=True, index=True)
    focus_duration_avg = Column(Float, default=2.0)         # Average focus session length in hours
    switch_tolerance = Column(Float, default=0.5)           # 0-1: tolerance for context switching
    consistency_score = Column(Float, default=0.5)          # 0-1: how regularly the operator works
    velocity_score = Column(Float, default=0.0)             # hours completed per day average
    total_slices_completed = Column(Integer, default=0)
    total_slices_abandoned = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DbNotificationLog(Base):
    """Log of all notifications sent. PRD §17.4"""
    __tablename__ = "notifications_log"

    id = Column(String, primary_key=True, index=True)
    operator_id = Column(String, nullable=False, index=True)
    notification_type = Column(String, nullable=False)      # timeslice_reminder | reflection_prompt | deadline_alert | weekly_summary
    channel = Column(String, nullable=False)                # desktop | telegram
    payload = Column(Text, default="{}")                    # JSON string with notification body
    sent_at = Column(DateTime, default=datetime.utcnow)
    delivered = Column(Boolean, default=True)


class DbTransaction(Base):
    __tablename__ = "sync_transactions"

    id = Column(String, primary_key=True, index=True)
    table_name = Column(String, nullable=False)  # "processes" or "time_slices"
    record_id = Column(String, nullable=False)
    action = Column(String, nullable=False)      # "INSERT", "UPDATE", "DELETE"
    payload = Column(String, default="{}")       # JSON serialised dump of the record
    created_at = Column(DateTime, default=datetime.utcnow)
    synced = Column(Boolean, default=False)


class DbCalendarEvent(Base):
    """Local calendar event store — holds both manually created events and Google-synced events. PRD §8.7"""
    __tablename__ = "calendar_events"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    description = Column(Text, default="")
    location = Column(String, default="")
    is_google_event = Column(Boolean, default=False)    # True if synced from Google Calendar
    google_event_id = Column(String, nullable=True)     # Google's event ID for upsert
    calendar_id = Column(String, default="primary")     # Google Calendar ID
    is_rest_period = Column(Boolean, default=False)     # True if this is a blocked rest period
    color = Column(String, default="primary")           # Display color hint
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DbUser(Base):
    """Local user account for JWT-based auth. Cognito-compatible schema. PRD §8.10"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    name = Column(String, default="")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
