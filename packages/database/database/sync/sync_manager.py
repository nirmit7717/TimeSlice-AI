import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from database.models import DbTransaction, DbProcess, DbTimeSlice
from database.sync.sync_models import SyncConflict

# Thread-safe in-memory cache to store pending conflicts during sync lifecycle
_conflicts_cache: Dict[str, SyncConflict] = {}

class SyncManager:
    """
    Manages local transactional logs and conflict resolution for synchronization with external PostgreSQL cloud storage.
    """
    def __init__(self, db: Session):
        self.db = db

    def get_pending_transactions(self) -> List[DbTransaction]:
        """
        Retrieves all transactions that have not yet been synchronized with the cloud.
        """
        return self.db.query(DbTransaction).filter(DbTransaction.synced == False).order_by(DbTransaction.created_at.asc()).all()

    def mark_as_synced(self, transaction_ids: List[str]) -> None:
        """
        Marks a list of transaction IDs as successfully synchronized.
        """
        if not transaction_ids:
            return
            
        self.db.query(DbTransaction).filter(DbTransaction.id.in_(transaction_ids)).update(
            {DbTransaction.synced: True},
            synchronize_session=False
        )
        self.db.commit()

    def clear_synced_transactions(self) -> int:
        """
        Cleans up and deletes all synced logs from the database to prevent storage bloat.
        Returns the count of deleted logs.
        """
        deleted_count = self.db.query(DbTransaction).filter(DbTransaction.synced == True).delete(synchronize_session=False)
        self.db.commit()
        return deleted_count

    def get_conflicts(self) -> List[SyncConflict]:
        """
        Returns all unresolved conflicts currently in the cache.
        """
        return list(_conflicts_cache.values())

    def pull_from_cloud(self, cloud_records: List[Dict[str, Any]]) -> List[SyncConflict]:
        """
        Pulls cloud changes, updates non-conflicting local records, and returns detected conflicts.
        """
        global _conflicts_cache
        new_conflicts = []

        # 1. Fetch pending unsynced local transaction IDs to check for concurrent writes
        pending_txs = self.get_pending_transactions()
        pending_map = {}
        for tx in pending_txs:
            pending_map[(tx.table_name, tx.record_id)] = tx

        for record in cloud_records:
            table_name = record.get("tableName")
            record_id = record.get("recordId")
            payload = record.get("payload", {})
            cloud_updated_at_str = record.get("updatedAt")
            
            if not table_name or not record_id:
                continue

            cloud_updated_at = (
                datetime.fromisoformat(cloud_updated_at_str)
                if cloud_updated_at_str
                else datetime.utcnow()
            )

            # Check if this record is currently conflicting locally
            conflict_key = f"{table_name}:{record_id}"

            # 2. Check if local record exists
            local_obj = None
            if table_name == "processes":
                local_obj = self.db.query(DbProcess).filter(DbProcess.id == record_id).first()
            elif table_name == "time_slices":
                local_obj = self.db.query(DbTimeSlice).filter(DbTimeSlice.id == record_id).first()

            # 3. Detect Conflicts
            has_pending_local = (table_name, record_id) in pending_map
            
            if local_obj:
                local_updated_at = getattr(local_obj, "updated_at", None) or getattr(local_obj, "created_at", None) or datetime.utcnow()
                
                if has_pending_local:
                    # Both sides have edits! Check if values actually differ
                    local_val = getattr(local_obj, "name", "") if table_name == "processes" else getattr(local_obj, "status", "")
                    cloud_val = payload.get("name", "") if table_name == "processes" else payload.get("status", "")
                    
                    if local_val != cloud_val:
                        # Conflict! Store in cache
                        process_name = getattr(local_obj, "name", "Focus Plan Window") if table_name == "processes" else "Focus Window"
                        conflict = SyncConflict(
                            id=conflict_key,
                            record_id=record_id,
                            table_name=table_name,
                            field="Name" if table_name == "processes" else "Status",
                            local_value=str(local_val),
                            cloud_value=str(cloud_val),
                            local_updated_at=local_updated_at,
                            cloud_updated_at=cloud_updated_at,
                            process_name=process_name
                        )
                        _conflicts_cache[conflict_key] = conflict
                        new_conflicts.append(conflict)
                        continue

            # 4. No conflict: safe to write latest cloud data locally
            if not has_pending_local:
                if table_name == "processes":
                    if not local_obj:
                        local_obj = DbProcess(id=record_id)
                        self.db.add(local_obj)
                    
                    # Update process fields
                    local_obj.name = payload.get("name", local_obj.name or "Cloud Process")
                    local_obj.description = payload.get("description", local_obj.description or "")
                    local_obj.goal = payload.get("goal", local_obj.goal or "")
                    local_obj.priority = payload.get("priority", local_obj.priority or 1)
                    local_obj.deadline = datetime.fromisoformat(payload.get("deadline")) if payload.get("deadline") else local_obj.deadline
                    local_obj.estimated_effort_hours = payload.get("estimatedEffortHours", local_obj.estimated_effort_hours or 0.0)
                    local_obj.remaining_effort_hours = payload.get("remainingEffortHours", local_obj.remaining_effort_hours or 0.0)
                    local_obj.status = payload.get("status", local_obj.status or "Active")
                    local_obj.progress = payload.get("progress", local_obj.progress or 0.0)
                    local_obj.updated_at = cloud_updated_at
                
                elif table_name == "time_slices":
                    if not local_obj:
                        local_obj = DbTimeSlice(id=record_id)
                        self.db.add(local_obj)
                    
                    # Update slice fields
                    local_obj.process_id = payload.get("processId", local_obj.process_id)
                    local_obj.start_time = datetime.fromisoformat(payload.get("startTime")) if payload.get("startTime") else local_obj.start_time
                    local_obj.end_time = datetime.fromisoformat(payload.get("endTime")) if payload.get("endTime") else local_obj.end_time
                    local_obj.duration_hours = payload.get("durationHours", local_obj.duration_hours or 1.0)
                    local_obj.status = payload.get("status", local_obj.status or "Scheduled")
                    local_obj.reflection = payload.get("reflection", local_obj.reflection)
                    local_obj.progress_gained = payload.get("progressGained", local_obj.progress_gained or 0.0)

        self.db.commit()
        return new_conflicts

    def resolve_conflict(self, conflict_id: str, resolution: str, cloud_payload: Optional[Dict[str, Any]] = None) -> bool:
        """
        Resolves a conflict using "local" (keep local version) or "cloud" (accept cloud version) policy.
        """
        global _conflicts_cache
        conflict = _conflicts_cache.get(conflict_id)
        if not conflict:
            return False

        table_name = conflict.table_name
        record_id = conflict.record_id

        if resolution == "cloud":
            # 1. Accept cloud values: update local DB
            payload = cloud_payload or {}
            if table_name == "processes":
                local_obj = self.db.query(DbProcess).filter(DbProcess.id == record_id).first()
                if local_obj:
                    local_obj.name = payload.get("name", local_obj.name)
                    local_obj.description = payload.get("description", local_obj.description)
                    local_obj.status = payload.get("status", local_obj.status)
                    local_obj.progress = payload.get("progress", local_obj.progress)
                    local_obj.updated_at = datetime.utcnow()
            elif table_name == "time_slices":
                local_obj = self.db.query(DbTimeSlice).filter(DbTimeSlice.id == record_id).first()
                if local_obj:
                    local_obj.status = payload.get("status", local_obj.status)
                    local_obj.reflection = payload.get("reflection", local_obj.reflection)

            # 2. Mark any pending local transactions for this record as synced (so they don't get pushed back to overwrite cloud)
            self.db.query(DbTransaction).filter(
                DbTransaction.table_name == table_name,
                DbTransaction.record_id == record_id,
                DbTransaction.synced == False
            ).update({DbTransaction.synced: True}, synchronize_session=False)
            self.db.commit()
            
        elif resolution == "local":
            # 1. Keep local values: local DB remains as is.
            # 2. Keep local transaction unsynced so that it will get pushed to the cloud in the next sync trigger.
            pass

        # Remove from active cache list
        if conflict_id in _conflicts_cache:
            del _conflicts_cache[conflict_id]
            
        return True
