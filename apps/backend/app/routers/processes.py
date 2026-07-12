import uuid
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from database.repositories.process_repo import ProcessRepository
from database.vector.vector_store import VectorStoreClient
from app.dependencies import get_process_repo, get_vector_store
from app.schemas import ProcessCreate, ProcessUpdate, ProcessResponse
from scheduling_system.models.process import Process, ProcessLifecycle

router = APIRouter(prefix="/processes", tags=["processes"])

@router.get("", response_model=List[ProcessResponse])
def list_processes(repo: ProcessRepository = Depends(get_process_repo)):
    return repo.list()

@router.get("/{process_id}", response_model=ProcessResponse)
def get_process(process_id: str, repo: ProcessRepository = Depends(get_process_repo)):
    p = repo.get(process_id)
    if not p:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Process with ID '{process_id}' not found"
        )
    return p

from database.repositories.slice_repo import TimeSliceRepository
from scheduling_system.services.scheduling_service import SchedulingService
from scheduling_system.models.time_slice import SliceStatus

def auto_recompute_plan(db):
    slice_repo = TimeSliceRepository(db)
    process_repo = ProcessRepository(db)
    
    # Clear scheduled slices
    existing_slices = slice_repo.list()
    for s in existing_slices:
        if s.status == SliceStatus.SCHEDULED:
            slice_repo.delete(s.id)
            
    # Generate new plan
    processes = process_repo.list()
    if not processes:
        return
    try:
        service = SchedulingService()
        plan = service.generate_execution_plan(
            processes=processes,
            calendar={"blocked_intervals": []},
            preferences={
                "max_daily_hours": 8.0,
                "quantum_hours": 2.0,
                "available_hours": 8.0
            },
            policy_name="round_robin"
        )
        for w in plan.execution_windows:
            slice_repo.create(w.time_slice)
    except Exception as e:
        print("[Auto-Recompute Error]", e)

@router.post("", response_model=ProcessResponse, status_code=status.HTTP_201_CREATED)
def create_process(
    payload: ProcessCreate,
    repo: ProcessRepository = Depends(get_process_repo),
    vector_client: VectorStoreClient = Depends(get_vector_store)
):
    pid = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    # 1. Map schema to domain model
    process_domain = Process(
        id=pid,
        name=payload.name,
        description=payload.description or "",
        goal=payload.goal or "",
        priority=payload.priority or 1,
        deadline=payload.deadline,
        estimated_effort_hours=payload.estimated_effort_hours,
        remaining_effort_hours=payload.remaining_effort_hours if payload.remaining_effort_hours is not None else payload.estimated_effort_hours,
        status=ProcessLifecycle(payload.status) if payload.status else ProcessLifecycle.ACTIVE,
        tags=payload.tags or [],
        dependency_ids=payload.dependency_ids or [],
        progress=0.0,
        health_score=100.0,
        attention_debt=0.0,
        attention_equity=0.0,
        created_at=now,
        updated_at=now
    )

    # 2. Database save
    saved = repo.create(process_domain)

    # 3. Vector store indexing
    doc_text = f"Process: {saved.name}. Description: {saved.description}. Goal: {saved.goal}"
    vector_client.add_document(
        doc_id=saved.id,
        text=doc_text,
        metadata={"priority": saved.priority, "status": saved.status.value}
    )

    # 4. Trigger auto-reschedule
    auto_recompute_plan(repo.db)

    return saved

@router.put("/{process_id}", response_model=ProcessResponse)
def update_process(
    process_id: str,
    payload: ProcessUpdate,
    repo: ProcessRepository = Depends(get_process_repo),
    vector_client: VectorStoreClient = Depends(get_vector_store)
):
    existing = repo.get(process_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Process with ID '{process_id}' not found"
        )

    # Update only provided attributes
    data = payload.model_dump(exclude_unset=True)
    for key, val in data.items():
        if hasattr(existing, key):
            setattr(existing, key, val)

    existing.updated_at = datetime.now(timezone.utc)
    
    # Re-save to DB
    updated = repo.update(existing)

    # Re-index in vector store if descriptive details changed
    if "name" in data or "description" in data or "goal" in data:
        doc_text = f"Process: {updated.name}. Description: {updated.description}. Goal: {updated.goal}"
        vector_client.add_document(
            doc_id=updated.id,
            text=doc_text,
            metadata={"priority": updated.priority, "status": updated.status.value}
        )

    # Trigger auto-reschedule
    auto_recompute_plan(repo.db)

    return updated

@router.delete("/{process_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_process(
    process_id: str,
    repo: ProcessRepository = Depends(get_process_repo),
    vector_client: VectorStoreClient = Depends(get_vector_store)
):
    success = repo.delete(process_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Process with ID '{process_id}' not found"
        )
    
    # Cascade delete from vector store
    vector_client.delete_document(process_id)

    # Trigger auto-reschedule
    auto_recompute_plan(repo.db)

