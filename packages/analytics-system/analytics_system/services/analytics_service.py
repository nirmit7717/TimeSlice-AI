from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from database.models import DbTimeSlice, DbProcess, DbAnalytics
from database.repositories.process_repo import ProcessRepository
from database.repositories.slice_repo import TimeSliceRepository
from scheduling_system.metrics.completion_velocity import CompletionVelocityCalculator
from scheduling_system.metrics.deadline_risk import DeadlineRiskCalculator
from scheduling_system.metrics.process_health import ProcessHealthCalculator
from scheduling_system.models.time_slice import SliceStatus
from analytics_system.models import WeeklySummary, FocusHoursEntry, TimeAllocationEntry

class AnalyticsService:
    def __init__(self, db_session):
        self.db = db_session
        self.process_repo = ProcessRepository(db_session)
        self.slice_repo = TimeSliceRepository(db_session)
        self.velocity_calc = CompletionVelocityCalculator()
        self.risk_calc = DeadlineRiskCalculator()
        self.health_calc = ProcessHealthCalculator()

    def refresh_analytics(self) -> List[DbAnalytics]:
        """
        Recalculates velocity, risk, health, status for all processes and persists to the analytics table.
        """
        processes = self.process_repo.list()
        all_slices = self.slice_repo.list()
        
        db_analytics_list = []
        for p in processes:
            # Filter slices for this process
            p_slices = [s for s in all_slices if s.process_id == p.id]
            completed_slices = [s for s in p_slices if s.status == SliceStatus.COMPLETED]
            
            # 1. Completion velocity (rolling 7 days)
            velocity = self.velocity_calc.calculate_velocity(completed_slices, rolling_window_days=7)
            
            # 2. Deadline risk
            risk = self.risk_calc.calculate_risk(
                remaining_effort_hours=p.remaining_effort_hours,
                deadline=p.deadline,
                velocity=velocity
            )
            
            # 3. Process Health & status
            health_score = p.health_score
            health_status = self.health_calc.get_health_status(health_score)
            
            # Upsert into DbAnalytics
            db_analytic = self.db.query(DbAnalytics).filter(DbAnalytics.process_id == p.id).first()
            if not db_analytic:
                db_analytic = DbAnalytics(
                    id=str(p.id),
                    process_id=p.id,
                    attention_debt=p.attention_debt,
                    attention_equity=p.attention_equity,
                    deadline_risk=risk,
                    completion_velocity=velocity,
                    process_health=health_score,
                    health_status=health_status,
                    last_computed_at=datetime.utcnow()
                )
                self.db.add(db_analytic)
            else:
                db_analytic.attention_debt = p.attention_debt
                db_analytic.attention_equity = p.attention_equity
                db_analytic.deadline_risk = risk
                db_analytic.completion_velocity = velocity
                db_analytic.process_health = health_score
                db_analytic.health_status = health_status
                db_analytic.last_computed_at = datetime.utcnow()
            
            db_analytics_list.append(db_analytic)
            
        self.db.commit()
        return db_analytics_list

    def get_focus_streak(self) -> int:
        """
        Calculates focus streak based on consecutive active days of completed slices.
        """
        all_slices = self.slice_repo.list()
        completed_dates = set()
        
        for s in all_slices:
            if s.status == SliceStatus.COMPLETED:
                completed_dates.add(s.start_time.date())
                
        if not completed_dates:
            return 0
            
        today = datetime.utcnow().date()
        streak = 0
        current_check = today
        
        while current_check in completed_dates:
            streak += 1
            current_check -= timedelta(days=1)
            
        # If no session today, check if there was one yesterday
        if streak == 0:
            current_check = today - timedelta(days=1)
            while current_check in completed_dates:
                streak += 1
                current_check -= timedelta(days=1)
                
        return streak

    def get_weekly_focus_hours(self) -> List[FocusHoursEntry]:
        """
        Aggregates completed session hours per day for the last 7 days.
        """
        all_slices = self.slice_repo.list()
        completed_slices = [s for s in all_slices if s.status == SliceStatus.COMPLETED]
        
        now = datetime.now()
        days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        
        daily_hours = {}
        for i in range(6, -1, -1):
            date = (now - timedelta(days=i)).date()
            daily_hours[date] = 0.0
            
        for s in completed_slices:
            s_date = s.start_time.date()
            if s_date in daily_hours:
                daily_hours[s_date] += s.duration_hours
                
        entries = []
        for date, hrs in daily_hours.items():
            day_name = days_of_week[date.weekday()]
            entries.append(FocusHoursEntry(day=day_name, hours=round(hrs, 1)))
            
        return entries

    def get_time_allocation(self) -> List[TimeAllocationEntry]:
        """
        Calculates total completed hours per process.
        """
        processes = self.process_repo.list()
        all_slices = self.slice_repo.list()
        completed_slices = [s for s in all_slices if s.status == SliceStatus.COMPLETED]
        
        process_map = {p.id: p.name for p in processes}
        allocation = {}
        
        for s in completed_slices:
            p_name = process_map.get(s.process_id, "Unknown Process")
            allocation[p_name] = allocation.get(p_name, 0.0) + s.duration_hours
            
        return [
            TimeAllocationEntry(name=name, hours=round(hrs, 1))
            for name, hrs in allocation.items()
        ]

    def get_weekly_summary(self) -> WeeklySummary:
        """
        Generates the standard WeeklySummary object.
        """
        streak = self.get_focus_streak()
        weekly_hours = self.get_weekly_focus_hours()
        time_alloc = self.get_time_allocation()
        
        total_hrs = sum(e.hours for e in weekly_hours)
        avg_hrs = total_hrs / 7.0 if total_hrs > 0 else 0.0
        
        return WeeklySummary(
            streak_days=streak,
            total_hours=round(total_hrs, 1),
            avg_hours_per_day=round(avg_hrs, 1),
            time_allocation=time_alloc,
            weekly_focus_hours=weekly_hours
        )
