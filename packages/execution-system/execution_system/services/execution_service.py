import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from database.models import DbTimeSlice, DbProcess, DbChecklist
from database.repositories.process_repo import ProcessRepository
from database.repositories.slice_repo import TimeSliceRepository
from scheduling_system.models.time_slice import SliceStatus
from execution_system.models import ChecklistItem

class ExecutionService:

    def __init__(self, db_session):
        self.db = db_session
        self.process_repo = ProcessRepository(db_session)
        self.slice_repo = TimeSliceRepository(db_session)

    def start_time_slice(self, process_id: str, duration_hours: float = 2.0) -> DbTimeSlice:
        """
        Starts a new focus session. Sets status to 'Active', maps to process,
        and generates initial checklist items if process is active.
        """
        # Verify process exists and is active
        proc = self.db.query(DbProcess).filter(DbProcess.id == process_id).first()
        if not proc:
            raise ValueError(f"Process with ID '{process_id}' does not exist")
            
        # Update process status if not active
        if proc.status in ["Created", "Paused"]:
            proc.status = "Active"
            proc.updated_at = datetime.utcnow()

        sid = str(uuid.uuid4())
        now = datetime.utcnow()
        db_slice = DbTimeSlice(
            id=sid,
            process_id=process_id,
            start_time=now,
            end_time=now + timedelta(hours=duration_hours), # end_time holds actual or scheduled end time
            duration_hours=duration_hours,
            status="Active",
            reflection=None,
            progress_gained=0.0,
            created_at=now
        )
        self.db.add(db_slice)
        
        # Generate default checklist items based on process goal
        default_items = [
            "Review session goals and prerequisites",
            "Deep focus implementation block",
            "Document progress and update remaining effort estimate"
        ]
        for idx, title in enumerate(default_items):
            item = DbChecklist(
                id=str(uuid.uuid4()),
                time_slice_id=sid,
                title=title,
                completed=False,
                order=idx,
                created_at=datetime.utcnow()
            )
            self.db.add(item)
            
        self.db.commit()
        self.db.refresh(db_slice)
        return db_slice

    def complete_time_slice(self, slice_id: str, progress_gained: float, reflection: str) -> DbTimeSlice:
        """
        Completes the session. Updates status, progress gained, and reflection.
        Increments parent process progress and updates metrics.
        """
        db_slice = self.db.query(DbTimeSlice).filter(DbTimeSlice.id == slice_id).first()
        if not db_slice:
            raise ValueError(f"Time slice '{slice_id}' not found")

        db_slice.status = "Completed"
        db_slice.progress_gained = progress_gained
        db_slice.reflection = reflection
        db_slice.end_time = datetime.utcnow()

        # Update process progress
        proc = self.db.query(DbProcess).filter(DbProcess.id == db_slice.process_id).first()
        if proc:
            proc.progress = min(1.0, max(0.0, proc.progress + progress_gained))
            proc.remaining_effort_hours = max(0.0, proc.remaining_effort_hours - db_slice.duration_hours)
            if proc.progress >= 1.0 or proc.remaining_effort_hours <= 0:
                proc.status = "Completed"
                proc.progress = 1.0
                proc.remaining_effort_hours = 0.0
            proc.updated_at = datetime.utcnow()
            
        self.db.commit()
        self.db.refresh(db_slice)

        # Fire adaptive learning event (Milestone 5.2)
        try:
            from adaptive_intelligence.learning_pipeline.learning_pipeline import LearningPipeline
            from adaptive_intelligence.models import LearningEvent, LearningEventType
            event_type = (
                LearningEventType.PROCESS_COMPLETED
                if proc and proc.status == "Completed"
                else LearningEventType.SESSION_COMPLETED
            )
            pipeline = LearningPipeline(self.db)
            pipeline.observe(LearningEvent(
                event_type=event_type,
                process_id=db_slice.process_id,
                slice_id=db_slice.id,
                context_features={"duration_hours": db_slice.duration_hours},
                timestamp=datetime.utcnow(),
            ))
        except Exception as e:
            print("[AdaptiveLearning Error]", e)

        return db_slice

    def abandon_time_slice(self, slice_id: str, reflection: str) -> DbTimeSlice:
        """
        Abandons the session, marking it as 'Abandoned'. Saves reasons/reflection.
        """
        db_slice = self.db.query(DbTimeSlice).filter(DbTimeSlice.id == slice_id).first()
        if not db_slice:
            raise ValueError(f"Time slice '{slice_id}' not found")

        db_slice.status = "Abandoned"
        db_slice.reflection = reflection
        db_slice.end_time = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_slice)

        # Fire adaptive learning event for abandonment (Milestone 5.2)
        try:
            from adaptive_intelligence.learning_pipeline.learning_pipeline import LearningPipeline
            from adaptive_intelligence.models import LearningEvent, LearningEventType
            pipeline = LearningPipeline(self.db)
            pipeline.observe(LearningEvent(
                event_type=LearningEventType.SESSION_ABANDONED,
                process_id=db_slice.process_id,
                slice_id=db_slice.id,
                context_features={"duration_hours": db_slice.duration_hours},
                timestamp=datetime.utcnow(),
            ))
        except Exception as e:
            print("[AdaptiveLearning Error]", e)

        return db_slice

    def get_checklists(self, slice_id: str) -> List[DbChecklist]:
        """
        Lists all checklist items for a session.
        """
        return self.db.query(DbChecklist).filter(DbChecklist.time_slice_id == slice_id).order_by(DbChecklist.order).all()

    def create_checklist_item(self, slice_id: str, title: str, order: int = 0) -> DbChecklist:
        """
        Adds a new checklist item to a session.
        """
        item = DbChecklist(
            id=str(uuid.uuid4()),
            time_slice_id=slice_id,
            title=title,
            completed=False,
            order=order,
            created_at=datetime.utcnow()
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def toggle_checklist_item(self, item_id: str) -> DbChecklist:
        """
        Toggles check status of a checklist item.
        """
        item = self.db.query(DbChecklist).filter(DbChecklist.id == item_id).first()
        if not item:
            raise ValueError(f"Checklist item '{item_id}' not found")
        item.completed = not item.completed
        self.db.commit()
        self.db.refresh(item)
        return item
