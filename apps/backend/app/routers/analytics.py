from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas import AnalyticsMetricsResponse, WeeklySummaryResponse
from analytics_system import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/metrics", response_model=List[AnalyticsMetricsResponse])
def get_metrics(db: Session = Depends(get_db)):
    """
    Triggers refresh of all process analytics and returns the persisted rows.
    """
    try:
        service = AnalyticsService(db)
        metrics = service.refresh_analytics()
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to load metrics: {str(e)}"
        )

@router.get("/health/{process_id}", response_model=AnalyticsMetricsResponse)
def get_process_health_analytics(process_id: str, db: Session = Depends(get_db)):
    """
    Fetches the specific analytics row for a process.
    """
    service = AnalyticsService(db)
    # Re-run refresh first to ensure accuracy
    service.refresh_analytics()
    
    from database.models import DbAnalytics
    metric = db.query(DbAnalytics).filter(DbAnalytics.process_id == process_id).first()
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No analytics found for process '{process_id}'"
        )
    return metric

@router.get("/focus-streak")
def get_focus_streak(db: Session = Depends(get_db)):
    """
    Calculates consecutive active focus days.
    """
    service = AnalyticsService(db)
    streak = service.get_focus_streak()
    return {"streakDays": streak}

@router.get("/time-allocation")
def get_time_allocation(db: Session = Depends(get_db)):
    """
    Returns time breakdown per process.
    """
    service = AnalyticsService(db)
    alloc = service.get_time_allocation()
    # Map to camelCase structure for frontend compatibility
    return [{"name": item.name, "hours": item.hours} for item in alloc]

@router.get("/weekly-summary", response_model=WeeklySummaryResponse)
def get_weekly_summary(db: Session = Depends(get_db)):
    """
    Generates full weekly digest.
    """
    try:
        service = AnalyticsService(db)
        summary = service.get_weekly_summary()
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to generate summary: {str(e)}"
        )
