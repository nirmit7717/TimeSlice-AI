import json
import uuid
from datetime import datetime
from typing import List, Optional
from database.models import DbTimeSlice, DbTransaction
from database.repositories.base import BaseRepository
from scheduling_system.models.time_slice import TimeSlice

class TimeSliceRepository(BaseRepository):
    def get(self, slice_id: str) -> Optional[TimeSlice]:
        """Retrieves a single time slice by its unique ID."""
        db_slice = self.db.query(DbTimeSlice).filter(DbTimeSlice.id == slice_id).first()
        return self._to_domain(db_slice) if db_slice else None

    def list(self) -> List[TimeSlice]:
        """Lists all time slices in the database."""
        db_slices = self.db.query(DbTimeSlice).all()
        return [self._to_domain(ds) for ds in db_slices]

    def list_by_process(self, process_id: str) -> List[TimeSlice]:
        """Lists all time slices allocated to a specific process."""
        db_slices = self.db.query(DbTimeSlice).filter(DbTimeSlice.process_id == process_id).all()
        return [self._to_domain(ds) for ds in db_slices]

    def create(self, time_slice: TimeSlice) -> TimeSlice:
        """Saves a new time slice record in the database."""
        data = time_slice.model_dump()
        db_slice = DbTimeSlice(**data)
        self.db.add(db_slice)
        
        self._log_transaction("time_slices", time_slice.id, "INSERT", data)
        self.db.commit()
        self.db.refresh(db_slice)
        return self._to_domain(db_slice)

    def update(self, time_slice: TimeSlice) -> TimeSlice:
        """Updates an existing time slice record in the database."""
        db_slice = self.db.query(DbTimeSlice).filter(DbTimeSlice.id == time_slice.id).first()
        if not db_slice:
            raise ValueError(f"Time slice with ID '{time_slice.id}' does not exist.")

        data = time_slice.model_dump()
        for key, val in data.items():
            if key != "id":
                setattr(db_slice, key, val)

        self._log_transaction("time_slices", time_slice.id, "UPDATE", data)
        self.db.commit()
        self.db.refresh(db_slice)
        return self._to_domain(db_slice)

    def delete(self, slice_id: str) -> bool:
        """Deletes a time slice by its ID."""
        db_slice = self.db.query(DbTimeSlice).filter(DbTimeSlice.id == slice_id).first()
        if not db_slice:
            return False
        self.db.delete(db_slice)
        self._log_transaction("time_slices", slice_id, "DELETE", {"id": slice_id})
        self.db.commit()
        return True

    def _log_transaction(self, table_name: str, record_id: str, action: str, payload: dict) -> None:
        def serialize_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError("Type not serializable")
            
        sync_tx = DbTransaction(
            id=str(uuid.uuid4()),
            table_name=table_name,
            record_id=record_id,
            action=action,
            payload=json.dumps(payload, default=serialize_datetime)
        )
        self.db.add(sync_tx)

    def _to_domain(self, db_slice: DbTimeSlice) -> TimeSlice:
        """Converts an internal database model instance to a clean domain Pydantic model."""
        return TimeSlice(
            id=db_slice.id,
            process_id=db_slice.process_id,
            start_time=db_slice.start_time,
            end_time=db_slice.end_time,
            duration_hours=db_slice.duration_hours,
            status=db_slice.status,
            reflection=db_slice.reflection,
            progress_gained=db_slice.progress_gained
        )
