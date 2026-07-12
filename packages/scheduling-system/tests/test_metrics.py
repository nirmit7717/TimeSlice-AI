import pytest
from datetime import datetime, timedelta, timezone
from scheduling_system.models.process import Process, ProcessLifecycle
from scheduling_system.metrics.attention_debt import AttentionDebtCalculator
from scheduling_system.metrics.attention_equity import AttentionEquityCalculator
from scheduling_system.metrics.process_health import ProcessHealthCalculator

def test_attention_debt_calculator():
    calc = AttentionDebtCalculator()
    p = Process(
        id="p1", name="Test", deadline=datetime.now(timezone.utc),
        estimated_effort_hours=10.0, remaining_effort_hours=5.0, priority=3
    )

    # 1. 0 days neglected
    now = datetime.now(timezone.utc)
    debt = calc.calculate_debt(p, now)
    assert debt == 0.0

    # 2. 5 days neglected
    five_days_ago = now - timedelta(days=5)
    debt = calc.calculate_debt(p, five_days_ago)
    # days = 5.0, priority_weight = 3 / 3 = 1.0, remaining_ratio = 5 / 10 = 0.5
    # debt = 5 * 1.0 * 0.5 = 2.5
    assert debt == 2.5

def test_attention_equity_calculator():
    calc = AttentionEquityCalculator()
    
    # 3 consecutive slices completed, 80% checklist completion rate (0.8)
    # equity = (3 * 3.0) + (0.8 * 10.0) = 9.0 + 8.0 = 17.0
    equity = calc.calculate_equity(3, 0.8)
    assert equity == 17.0

def test_process_health_calculator():
    calc = ProcessHealthCalculator()
    p = Process(
        id="p1", name="Test", deadline=datetime.now(timezone.utc) + timedelta(days=2),
        estimated_effort_hours=10.0, remaining_effort_hours=4.0, priority=3,
        attention_debt=2.0, attention_equity=10.0
    )

    # Health score starts at 100.0
    # Penalty for debt: min(35.0, 2.0 * 2.5) = 5.0
    # Bonus for equity: min(15.0, 10.0 * 0.20) = 2.0
    # No deadline penalty (time left 48h > remaining 4h)
    # Score = 100 - 5.0 + 2.0 = 97.0
    score = calc.calculate_health_score(p, time_left_hours=48.0)
    assert score == 97.0
    assert calc.get_health_status(score) == "Excellent"

    # Deficit check (remaining effort 4.0, but only 2.0 hours left before deadline)
    # Deficit = 4.0 - 2.0 = 2.0
    # deadline_penalty = min(50.0, (2.0 / 4.0) * 50.0) = 25.0
    # Score = 100.0 - 5.0 (debt) + 2.0 (equity) - 25.0 (deadline) = 72.0
    score_deficient = calc.calculate_health_score(p, time_left_hours=2.0)
    assert score_deficient == 72.0
    assert calc.get_health_status(score_deficient) == "Fair"


from scheduling_system.metrics.completion_velocity import CompletionVelocityCalculator
from scheduling_system.metrics.deadline_risk import DeadlineRiskCalculator
from scheduling_system.models.time_slice import TimeSlice, SliceStatus

def test_completion_velocity_calculator():
    calc = CompletionVelocityCalculator()
    now = datetime.now(timezone.utc)
    
    slices = [
        TimeSlice(id="s1", process_id="p1", start_time=now - timedelta(hours=3), end_time=now - timedelta(hours=2), duration_hours=1.0, status=SliceStatus.COMPLETED),
        TimeSlice(id="s2", process_id="p1", start_time=now - timedelta(hours=2), end_time=now - timedelta(hours=1), duration_hours=2.0, status=SliceStatus.COMPLETED),
        TimeSlice(id="s3", process_id="p1", start_time=now - timedelta(days=10), end_time=now - timedelta(days=9), duration_hours=3.0, status=SliceStatus.COMPLETED), # Out of 7-day window
    ]
    
    velocity = calc.calculate_velocity(slices, rolling_window_days=7)
    # Total hours in last 7 days = 1.0 (s1) + 2.0 (s2) = 3.0
    # Velocity = 3.0 / 7 = 0.43
    assert velocity == 0.43

def test_deadline_risk_calculator():
    calc = DeadlineRiskCalculator()
    now = datetime.now(timezone.utc)
    
    # 1. Overdue -> Critical
    risk = calc.calculate_risk(remaining_effort_hours=5.0, deadline=now - timedelta(hours=1))
    assert risk == "Critical"
    
    # 2. Tight timeline -> Critical (needs 10h in 1 day, daily capacity is 8h)
    risk = calc.calculate_risk(remaining_effort_hours=10.0, deadline=now + timedelta(days=1))
    assert risk == "Critical"
    
    # 3. High risk (needs 7h in 1 day, daily capacity is 8h)
    risk = calc.calculate_risk(remaining_effort_hours=7.0, deadline=now + timedelta(days=1))
    assert risk == "High"
    
    # 4. Low risk (needs 1h in 2 days)
    risk = calc.calculate_risk(remaining_effort_hours=1.0, deadline=now + timedelta(days=2))
    assert risk == "Low"

