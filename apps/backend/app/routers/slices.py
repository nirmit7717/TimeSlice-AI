import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from database.repositories.slice_repo import TimeSliceRepository
from app.dependencies import get_slice_repo
from app.schemas import TimeSliceCreate, TimeSliceResponse
from scheduling_system.models.time_slice import TimeSlice, SliceStatus

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
