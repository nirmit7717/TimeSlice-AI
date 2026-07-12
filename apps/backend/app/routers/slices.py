import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.repositories.slice_repo import TimeSliceRepository
from app.dependencies import get_slice_repo, get_db
from app.schemas import (
    TimeSliceCreate, TimeSliceResponse, StartSliceRequest,
    CompleteSliceRequest, AbandonSliceRequest, ChecklistItemResponse,
    CreateChecklistItemRequest
)
from scheduling_system.models.time_slice import TimeSlice, SliceStatus
from execution_system import ExecutionService

router = APIRouter(prefix="/slices", tags=["slices"])

@router.get("", response_model=List[TimeSliceResponse])
def list_slices(
    process_id: Optional[str] = None,
    repo: TimeSliceRepository = Depends(get_slice_repo)
):
    if process_id:
        return repo.list_by_process(process_id)
    return repo.list()

@router.get("/{slice_id}", response_model=TimeSliceResponse)
def get_slice(slice_id: str, repo: TimeSliceRepository = Depends(get_slice_repo)):
    ts = repo.get(slice_id)
    if not ts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Time slice with ID '{slice_id}' not found"
        )
    return ts

@router.post("", response_model=TimeSliceResponse, status_code=status.HTTP_201_CREATED)
def create_slice(payload: TimeSliceCreate, repo: TimeSliceRepository = Depends(get_slice_repo)):
    sid = str(uuid.uuid4())
    slice_domain = TimeSlice(
        id=sid,
        process_id=payload.process_id,
        start_time=payload.start_time,
        end_time=payload.end_time,
        duration_hours=payload.duration_hours,
        status=SliceStatus(payload.status) if payload.status else SliceStatus.SCHEDULED,
        reflection=payload.reflection,
        progress_gained=payload.progress_gained or 0.0
    )
    return repo.create(slice_domain)

@router.delete("/{slice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_slice(slice_id: str, repo: TimeSliceRepository = Depends(get_slice_repo)):
    success = repo.delete(slice_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Time slice with ID '{slice_id}' not found"
        )

@router.post("/start", response_model=TimeSliceResponse, status_code=status.HTTP_201_CREATED)
def start_slice(payload: StartSliceRequest, db: Session = Depends(get_db)):
    """Starts a new active session."""
    try:
        service = ExecutionService(db)
        return service.start_time_slice(payload.process_id, payload.duration_hours)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/{slice_id}/complete", response_model=TimeSliceResponse)
def complete_slice(slice_id: str, payload: CompleteSliceRequest, db: Session = Depends(get_db)):
    """Completes an active session."""
    try:
        service = ExecutionService(db)
        return service.complete_time_slice(slice_id, payload.progress_gained, payload.reflection)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/{slice_id}/abandon", response_model=TimeSliceResponse)
def abandon_slice(slice_id: str, payload: AbandonSliceRequest, db: Session = Depends(get_db)):
    """Abandons an active session."""
    try:
        service = ExecutionService(db)
        return service.abandon_time_slice(slice_id, payload.reflection)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{slice_id}/checklists", response_model=List[ChecklistItemResponse])
def get_checklists(slice_id: str, db: Session = Depends(get_db)):
    """Lists all checklist items for a session."""
    service = ExecutionService(db)
    return service.get_checklists(slice_id)

@router.post("/{slice_id}/checklists", response_model=ChecklistItemResponse, status_code=status.HTTP_201_CREATED)
def create_checklist_item(slice_id: str, payload: CreateChecklistItemRequest, db: Session = Depends(get_db)):
    """Adds a new checklist item to a session."""
    service = ExecutionService(db)
    return service.create_checklist_item(slice_id, payload.title, payload.order)

@router.patch("/checklists/{item_id}", response_model=ChecklistItemResponse)
def toggle_checklist_item(item_id: str, db: Session = Depends(get_db)):
    """Toggles checklist item completed status."""
    try:
        service = ExecutionService(db)
        return service.toggle_checklist_item(item_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

