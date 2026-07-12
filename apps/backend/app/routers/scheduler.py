from datetime import datetime, timezone
import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from database.repositories.process_repo import ProcessRepository
from database.repositories.slice_repo import TimeSliceRepository
from app.dependencies import get_process_repo, get_slice_repo
from app.schemas import (
    PlanRequest, ExecutionPlanResponse, RescheduleRequest,
    SimulationRequest, SimulationResponse, ProcessResponse,
    RecommendationResponse
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


@router.get("/simulate", response_model=List[SimulationResponse])
def simulate_all_policies(
    quantum_hours: float = 2.0,
    available_hours: float = 8.0,
    process_repo: ProcessRepository = Depends(get_process_repo)
):
    processes = process_repo.list()
    if not processes:
        return []

    constraints = {
        "blocked_intervals": [],
        "quantum_hours": quantum_hours,
        "available_hours": available_hours
    }

    policies = ["round_robin", "priority", "sjf", "edf"]
    results = []
    for policy in policies:
        try:
            res = service.simulate_policy(
                policy_name=policy,
                processes=processes,
                constraints=constraints
            )
            results.append(res)
        except Exception as e:
            # Skip failed policy simulation
            continue
    return results


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


@router.get("/plan", response_model=ExecutionPlanResponse)
def get_current_plan(
    policy_name: str = "round_robin",
    quantum_hours: float = 2.0,
    available_hours: float = 8.0,
    process_repo: ProcessRepository = Depends(get_process_repo),
    slice_repo: TimeSliceRepository = Depends(get_slice_repo)
):
    # 1. Load active time slices from DB
    slices = slice_repo.list()
    # Filter only scheduled/active slices
    scheduled_slices = [s for s in slices if s.status in [SliceStatus.SCHEDULED, "Active"]]
    
    if scheduled_slices:
        # Reconstruct execution windows
        windows = [
            ExecutionWindow(id=s.id, time_slice=s)
            for s in scheduled_slices
        ]
        # Sort chronologically
        windows.sort(key=lambda w: w.time_slice.start_time)
        return ExecutionPlan(
            id=str(uuid.uuid4()),
            policy_name=policy_name,
            time_quantum_hours=quantum_hours,
            execution_windows=windows,
            created_at=datetime.now(timezone.utc)
        )
    
    # If no plan exists, generate one automatically
    processes = process_repo.list()
    if not processes:
        return ExecutionPlan(
            id=str(uuid.uuid4()),
            policy_name=policy_name,
            time_quantum_hours=quantum_hours,
            execution_windows=[],
            created_at=datetime.now(timezone.utc)
        )
        
    try:
        plan = service.generate_execution_plan(
            processes=processes,
            calendar={"blocked_intervals": []},
            preferences={
                "max_daily_hours": 8.0,
                "quantum_hours": quantum_hours,
                "available_hours": available_hours
            },
            policy_name=policy_name
        )
        # Save generated time slices to DB so they persist
        for w in plan.execution_windows:
            slice_repo.create(w.time_slice)
        return plan
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/recompute", response_model=ExecutionPlanResponse)
def recompute_plan(
    policy_name: str = "round_robin",
    quantum_hours: float = 2.0,
    available_hours: float = 8.0,
    process_repo: ProcessRepository = Depends(get_process_repo),
    slice_repo: TimeSliceRepository = Depends(get_slice_repo)
):
    # 1. Clear existing scheduled slices in DB
    existing_slices = slice_repo.list()
    for s in existing_slices:
        if s.status == SliceStatus.SCHEDULED:
            slice_repo.delete(s.id)
            
    # 2. Generate a new plan
    processes = process_repo.list()
    if not processes:
        return ExecutionPlan(
            id=str(uuid.uuid4()),
            policy_name=policy_name,
            time_quantum_hours=quantum_hours,
            execution_windows=[],
            created_at=datetime.now(timezone.utc)
        )
        
    try:
        plan = service.generate_execution_plan(
            processes=processes,
            calendar={"blocked_intervals": []},
            preferences={
                "max_daily_hours": 8.0,
                "quantum_hours": quantum_hours,
                "available_hours": available_hours
            },
            policy_name=policy_name
        )
        # 3. Save new slices
        for w in plan.execution_windows:
            slice_repo.create(w.time_slice)
        return plan
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/recommendation", response_model=RecommendationResponse)
def get_recommendation(
    process_repo: ProcessRepository = Depends(get_process_repo),
    slice_repo: TimeSliceRepository = Depends(get_slice_repo)
):
    processes = process_repo.list()
    if not processes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active processes available to recommend"
        )
        
    # Recompute metrics first to make sure debt/health/equity are up to date
    # Simple reuse of compute_metrics endpoint logic locally:
    last_slice_dates = {}
    history_stats = {}
    for p in processes:
        slices = slice_repo.list_by_process(p.id)
        completed_slices = [s for s in slices if s.status == SliceStatus.COMPLETED]
        if completed_slices:
            completed_slices.sort(key=lambda x: x.end_time)
            last_slice_dates[p.id] = completed_slices[-1].end_time
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
            
    updated_procs = service.compute_metrics(processes, last_slice_dates, history_stats)
    
    # Save updated metrics to DB
    for p in updated_procs:
        process_repo.update(p)

    # Filter to only Active/Created processes
    active_procs = [p for p in updated_procs if p.status in ["Active", "Created"]]
    if not active_procs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active processes found to recommend"
        )

    # Pick top process: sort by priority desc, attention debt desc, then deadline asc
    # Attention debt indicates neglect, priority indicates user importance.
    active_procs.sort(key=lambda x: (-x.priority, -x.attention_debt, x.deadline))
    top_process = active_procs[0]
    
    # Build explanation reasons
    reasons = []
    # Reason 1: Priority
    if top_process.priority >= 4:
        reasons.append(f"High priority process ({top_process.priority}/5)")
    else:
        reasons.append(f"Standard priority process")
        
    # Reason 2: Attention Debt
    if top_process.attention_debt > 2.0:
        reasons.append(f"High Attention Debt accumulated ({round(top_process.attention_debt, 1)}h)")
    
    # Reason 3: Deadline
    now_naive = datetime.utcnow()
    p_deadline = top_process.deadline.replace(tzinfo=None) if top_process.deadline else None
    if p_deadline:
        hours_left = (p_deadline - now_naive).total_seconds() / 3600.0
        if hours_left <= 48:
            reasons.append(f"Deadline approaching in {round(hours_left, 1)} hours")
        else:
            days_left = hours_left / 24.0
            reasons.append(f"Deadline approaching in {round(days_left, 1)} days")
            
    # Reason 4: Focus window matching
    reasons.append("Best focus window based on your history")

    # Confidence calculation: starts at 90%, drops if priority low or deadline far
    confidence = 0.90
    if top_process.priority < 3:
        confidence -= 0.10
    if p_deadline and (p_deadline - now_naive).days > 7:
        confidence -= 0.05
    confidence = max(0.50, min(0.99, confidence))

    return RecommendationResponse(
        process_name=top_process.name,
        process_id=top_process.id,
        policy_name="round_robin",
        duration_hours=2.0,
        deadline=top_process.deadline,
        priority=top_process.priority,
        attention_debt=top_process.attention_debt,
        confidence_score=confidence,
        reasons=reasons
    )

