from datetime import datetime, timezone
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from database.repositories.process_repo import ProcessRepository
from database.repositories.slice_repo import TimeSliceRepository
from app.dependencies import get_process_repo, get_slice_repo
from app.schemas import (
    PlanRequest, ExecutionPlanResponse, RescheduleRequest,
    SimulationRequest, SimulationResponse, ProcessResponse
)
from scheduling_system.services.scheduling_service import SchedulingService
from scheduling_system.models.execution_plan import ExecutionPlan, ExecutionWindow
from scheduling_system.models.time_slice import TimeSlice, SliceStatus

router = APIRouter(prefix="/scheduler", tags=["scheduler"])
service = SchedulingService()

@router.post("/plan", response_model=ExecutionPlanResponse)
def generate_plan(
    payload: PlanRequest,
    process_repo: ProcessRepository = Depends(get_process_repo)
):
    # 1. Load processes from DB
    processes = process_repo.list()
    if not processes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No processes found in database. Cannot generate plan."
        )

    # 2. Format context constraints
    blocked = []
    if payload.blocked_intervals:
        for interval in payload.blocked_intervals:
            if len(interval) == 2:
                blocked.append((interval[0], interval[1]))

    calendar = {"blocked_intervals": blocked}
    preferences = {
        "max_daily_hours": 8.0, # default constraint limit
        "quantum_hours": payload.quantum_hours,
        "available_hours": payload.available_hours
    }

    # 3. Generate plan via Facade Service
    try:
        plan = service.generate_execution_plan(
            processes=processes,
            calendar=calendar,
            preferences=preferences,
            policy_name=payload.policy_name
        )
        return plan
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/reschedule", response_model=ExecutionPlanResponse)
def reschedule_plan(
    payload: Dict[str, Any], # Accept flexible JSON and decode manually to avoid complex nested Pydantic issues
    process_repo: ProcessRepository = Depends(get_process_repo)
):
    """
    Executes localized rescheduling. Expects keys: 'currentPlan' and 'event' (RescheduleRequest).
    """
    current_plan_data = payload.get("currentPlan")
    event_data = payload.get("event")
    
    if not current_plan_data or not event_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payload must contain both 'currentPlan' and 'event' keys."
        )

    try:
        # Reconstruct current plan model
        windows = []
        for w in current_plan_data.get("executionWindows", []):
            ts_data = w.get("timeSlice")
            ts = TimeSlice(
                id=ts_data.get("id"),
                process_id=ts_data.get("processId"),
                start_time=datetime.fromisoformat(ts_data.get("startTime")),
                end_time=datetime.fromisoformat(ts_data.get("endTime")),
                duration_hours=ts_data.get("durationHours"),
                status=SliceStatus(ts_data.get("status")),
                reflection=ts_data.get("reflection"),
                progress_gained=ts_data.get("progressGained", 0.0)
            )
            windows.append(ExecutionWindow(id=w.get("id"), time_slice=ts))

        current_plan = ExecutionPlan(
            id=current_plan_data.get("id"),
            policy_name=current_plan_data.get("policyName"),
            time_quantum_hours=current_plan_data.get("timeQuantumHours"),
            execution_windows=windows,
            created_at=datetime.fromisoformat(current_plan_data.get("createdAt"))
        )

        # Decode event
        event = {
            "event_type": event_data.get("eventType"),
            "start_time": datetime.fromisoformat(event_data.get("startTime")),
            "end_time": datetime.fromisoformat(event_data.get("endTime"))
        }

        # Run rescheduling
        updated_plan = service.recompute_execution_plan(current_plan, event, context={"blocked_intervals": []})
        return updated_plan
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rescheduling failed: {str(e)}"
        )

@router.post("/simulate", response_model=SimulationResponse)
def simulate_policy(
    payload: SimulationRequest,
    process_repo: ProcessRepository = Depends(get_process_repo)
):
    processes = process_repo.list()
    if not processes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No processes found in database. Cannot run simulation."
        )

    constraints = {
        "blocked_intervals": [],
        "quantum_hours": payload.quantum_hours,
        "available_hours": payload.available_hours
    }

    try:
        res = service.simulate_policy(
            policy_name=payload.policy_name,
            processes=processes,
            constraints=constraints
        )
        return res
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Simulation failed: {str(e)}"
        )

@router.get("/metrics", response_model=List[ProcessResponse])
def compute_metrics(
    process_repo: ProcessRepository = Depends(get_process_repo),
    slice_repo: TimeSliceRepository = Depends(get_slice_repo)
):
    """
    Recalculates scheduling metrics for all processes, saves them to database, and returns updated objects.
    """
    processes = process_repo.list()
    if not processes:
        return []

    # Assemble historical stats and last slice executions
    last_slice_dates = {}
    history_stats = {}

    for p in processes:
        slices = slice_repo.list_by_process(p.id)
        
        # Sort chronologically to find last slice
        completed_slices = [s for s in slices if s.status == SliceStatus.COMPLETED]
        if completed_slices:
            completed_slices.sort(key=lambda x: x.end_time)
            last_slice_dates[p.id] = completed_slices[-1].end_time
            
            # Find consecutive completed slices
            # Let's count consecutive completed slices in all slices sorted by time
            slices.sort(key=lambda x: x.end_time)
            consec = 0
            for s in reversed(slices):
                if s.status == SliceStatus.COMPLETED:
                    consec += 1
                else:
                    break
            
            rate = len(completed_slices) / len(slices)
            history_stats[p.id] = {
                "consecutive_completed": consec,
                "checklist_completion_rate": rate
            }
        else:
            last_slice_dates[p.id] = None
            history_stats[p.id] = {
                "consecutive_completed": 0,
                "checklist_completion_rate": 0.0
            }

    # Run metrics calculation
    updated_procs = service.compute_metrics(processes, last_slice_dates, history_stats)

    # Save changes to SQL DB
    for p in updated_procs:
        process_repo.update(p)

    return updated_procs
