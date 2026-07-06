import json
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, TypeDecorator
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

class DbTimeSlice(Base):
    __tablename__ = "time_slices"

    id = Column(String, primary_key=True, index=True)
    process_id = Column(String, ForeignKey("processes.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    duration_hours = Column(Float, nullable=False)
    status = Column(String, default="Scheduled")
    reflection = Column(String, nullable=True)
    progress_gained = Column(Float, default=0.0)

    # Relationships
    process = relationship("DbProcess", back_populates="time_slices")
