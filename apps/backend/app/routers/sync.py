from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from database.sync.sync_manager import SyncManager
from app.dependencies import get_sync_manager, get_db
from app.schemas import CamelModel
from platform_services.background.bg_sync import BackgroundSyncService

router = APIRouter(prefix="/sync", tags=["sync"])
bg_sync_service = BackgroundSyncService()

class ConfirmSyncRequest(CamelModel):
    transaction_ids: List[str]

class TriggerSyncRequest(CamelModel):
    cloud_endpoint: str

@router.get("/pending")
def get_pending_logs(sync_mgr: SyncManager = Depends(get_sync_manager)):
    """
    Returns the list of local write transaction logs waiting to sync.
    """
    logs = sync_mgr.get_pending_transactions()
    return [
        {
            "id": l.id,
            "tableName": l.table_name,
            "recordId": l.record_id,
            "action": l.action,
            "payload": l.payload,
            "createdAt": l.created_at
        }
        for l in logs
    ]

@router.post("/confirm")
def confirm_synced_logs(
    payload: ConfirmSyncRequest,
    sync_mgr: SyncManager = Depends(get_sync_manager)
):
    """
    Marks local logs as synced after positive cloud verification.
    """
    sync_mgr.mark_as_synced(payload.transaction_ids)
    return {"status": "success", "confirmedCount": len(payload.transaction_ids)}

@router.post("/trigger")
def trigger_manual_sync(
    payload: TriggerSyncRequest,
    db_session = Depends(get_db)
):
    """
    Triggers a manual background worker loop execution to the cloud server.
    """
    try:
        from database.connection import SessionLocal
        # Run a one-off sync loop invocation in thread pool
        sync_mgr = SyncManager(db_session)
        pending = sync_mgr.get_pending_transactions()
        
        synced_ids = []
        for tx in pending:
            # Replicate to target
            success = bg_sync_service._push_to_cloud(tx, payload.cloud_endpoint)
            if success:
                synced_ids.append(tx.id)
                
        if synced_ids:
            sync_mgr.mark_as_synced(synced_ids)
            
        return {"status": "success", "syncedCount": len(synced_ids), "syncedIds": synced_ids}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync trigger failed: {str(e)}"
        )


class PullSyncRequest(CamelModel):
    cloud_records: List[Dict[str, Any]]


class ResolveConflictRequest(CamelModel):
    resolution: str  # "local" | "cloud"
    cloud_payload: Optional[Dict[str, Any]] = None


@router.post("/pull")
def pull_changes(
    payload: PullSyncRequest,
    sync_mgr: SyncManager = Depends(get_sync_manager)
):
    """
    Accepts cloud records, updates local database, and returns detected conflicts.
    """
    conflicts = sync_mgr.pull_from_cloud(payload.cloud_records)
    # Convert conflict models to camelCase output structures
    return [
        {
            "id": c.id,
            "recordId": c.record_id,
            "tableName": c.table_name,
            "field": c.field,
            "localValue": c.local_value,
            "cloudValue": c.cloud_value,
            "localUpdatedAt": c.local_updated_at.isoformat(),
            "cloudUpdatedAt": c.cloud_updated_at.isoformat(),
            "processName": c.process_name
        }
        for c in conflicts
    ]


@router.get("/conflicts")
def get_conflicts(sync_mgr: SyncManager = Depends(get_sync_manager)):
    """
    Retrieves all unresolved conflicts.
    """
    conflicts = sync_mgr.get_conflicts()
    return [
        {
            "id": c.id,
            "recordId": c.record_id,
            "tableName": c.table_name,
            "field": c.field,
            "localValue": c.local_value,
            "cloudValue": c.cloud_value,
            "localUpdatedAt": c.local_updated_at.isoformat(),
            "cloudUpdatedAt": c.cloud_updated_at.isoformat(),
            "processName": c.process_name
        }
        for c in conflicts
    ]


@router.post("/conflicts/{conflict_id}/resolve")
def resolve_conflict(
    conflict_id: str,
    payload: ResolveConflictRequest,
    sync_mgr: SyncManager = Depends(get_sync_manager)
):
    """
    Resolves a specific conflict.
    """
    success = sync_mgr.resolve_conflict(
        conflict_id,
        payload.resolution,
        payload.cloud_payload
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conflict '{conflict_id}' not found."
        )
    return {"status": "success", "message": f"Conflict resolved using {payload.resolution} resolution."}


@router.get("/status")
def get_sync_status(sync_mgr: SyncManager = Depends(get_sync_manager)):
    """
    Returns sync statistics (pending count, conflicts count).
    """
    pending = sync_mgr.get_pending_transactions()
    conflicts = sync_mgr.get_conflicts()
    
    # We retrieve last_synced_at from database transactions where synced = True
    # (ordered by created_at desc)
    from database.models import DbTransaction
    last_tx = sync_mgr.db.query(DbTransaction).filter(DbTransaction.synced == True).order_by(DbTransaction.created_at.desc()).first()
    last_synced_at = last_tx.created_at.isoformat() if last_tx else None

    return {
        "lastSyncedAt": last_synced_at,
        "pendingCount": len(pending),
        "conflictCount": len(conflicts),
        "isOnline": True  # local simulation status is always online
    }

