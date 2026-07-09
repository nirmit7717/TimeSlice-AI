import json
import uuid
from datetime import datetime
from typing import List, Optional
from database.models import DbProcess, DbTransaction
from database.repositories.base import BaseRepository
from scheduling_system.models.process import Process

class ProcessRepository(BaseRepository):
    def get(self, process_id: str) -> Optional[Process]:
        """Retrieves a single process by its unique ID."""
        db_proc = self.db.query(DbProcess).filter(DbProcess.id == process_id).first()
        return self._to_domain(db_proc) if db_proc else None

    def list(self) -> List[Process]:
        """Lists all processes in the database."""
        db_procs = self.db.query(DbProcess).all()
        return [self._to_domain(dp) for dp in db_procs]

    def create(self, process: Process) -> Process:
        """Saves a new process record in the database."""
        data = process.model_dump()
        db_proc = DbProcess(**data)
        self.db.add(db_proc)
        
        self._log_transaction("processes", process.id, "INSERT", data)
        self.db.commit()
        self.db.refresh(db_proc)
        return self._to_domain(db_proc)

    def update(self, process: Process) -> Process:
        """Updates an existing process record in the database."""
        db_proc = self.db.query(DbProcess).filter(DbProcess.id == process.id).first()
        if not db_proc:
            raise ValueError(f"Process with ID '{process.id}' does not exist.")

        data = process.model_dump()
        for key, val in data.items():
            if key != "id":
                setattr(db_proc, key, val)

        self._log_transaction("processes", process.id, "UPDATE", data)
        self.db.commit()
        self.db.refresh(db_proc)
        return self._to_domain(db_proc)

    def delete(self, process_id: str) -> bool:
        """Deletes a process by its ID. Cascade deletes associated time slices."""
        db_proc = self.db.query(DbProcess).filter(DbProcess.id == process_id).first()
        if not db_proc:
            return False
        self.db.delete(db_proc)
        self._log_transaction("processes", process_id, "DELETE", {"id": process_id})
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


    def _to_domain(self, db_proc: DbProcess) -> Process:
        """Converts an internal database model instance to a clean domain Pydantic model."""
        return Process(
            id=db_proc.id,
            name=db_proc.name,
            description=db_proc.description,
            goal=db_proc.goal,
            priority=db_proc.priority,
            deadline=db_proc.deadline,
            estimated_effort_hours=db_proc.estimated_effort_hours,
            remaining_effort_hours=db_proc.remaining_effort_hours,
            status=db_proc.status,
            tags=db_proc.tags,
            dependency_ids=db_proc.dependency_ids,
            progress=db_proc.progress,
            health_score=db_proc.health_score,
            attention_debt=db_proc.attention_debt,
            attention_equity=db_proc.attention_equity,
            created_at=db_proc.created_at,
            updated_at=db_proc.updated_at
        )
