from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from scheduling_system.interfaces.service import ISchedulingService
from scheduling_system.models.process import Process
from scheduling_system.models.execution_plan import ExecutionPlan
from scheduling_system.analyzer.process_analyzer import ProcessAnalyzer
from scheduling_system.constraints.constraint_engine import ConstraintEngine
from scheduling_system.policy.policy_manager import PolicyManager
from scheduling_system.planner.execution_planner import ExecutionPlanner
from scheduling_system.rescheduler.dynamic_rescheduler import DynamicRescheduler
from scheduling_system.simulator.simulator import SchedulerSimulator
from scheduling_system.metrics.attention_debt import AttentionDebtCalculator
from scheduling_system.metrics.attention_equity import AttentionEquityCalculator
from scheduling_system.metrics.process_health import ProcessHealthCalculator

class SchedulingService(ISchedulingService):
    def __init__(self):
        self.analyzer = ProcessAnalyzer()
        self.constraint_engine = ConstraintEngine()
        self.policy_manager = PolicyManager()
        self.planner = ExecutionPlanner()
        self.rescheduler = DynamicRescheduler()
        self.simulator = SchedulerSimulator()
        
        self.debt_calc = AttentionDebtCalculator()
        self.equity_calc = AttentionEquityCalculator()
        self.health_calc = ProcessHealthCalculator()

    def generate_execution_plan(
        self,
        processes: List[Process],
        calendar: Any,
        preferences: Any,
        policy_name: str
    ) -> ExecutionPlan:
        """
        Coordinates process analysis, constraints package mapping, and planner execution.
        """
        # 1. Validate active processes
        active_processes = self.analyzer.validate_processes(processes)
        
        # 2. Resolve policy
        policy = self.policy_manager.get_policy(policy_name)
        
        # 3. Create context from parameters
        max_daily_hours = preferences.get("max_daily_hours", 8.0) if preferences else 8.0
        quantum_hours = preferences.get("quantum_hours", 2.0) if preferences else 2.0
        available_hours = preferences.get("available_hours", 24.0) if preferences else 24.0
        blocked_intervals = calendar.get("blocked_intervals", []) if calendar else []
        
        context = {
            "processes": active_processes,
            "blocked_intervals": blocked_intervals,
            "max_daily_hours": max_daily_hours
        }

        # 4. Generate plan
        return self.planner.plan(active_processes, policy, quantum_hours, available_hours, context)

    def recompute_execution_plan(
        self,
        current_plan: ExecutionPlan,
        scheduling_event: Any,
        context: Any = None
    ) -> ExecutionPlan:
        """
        Wrapper around the dynamic rescheduler.
        """
        if context is None:
            context = {"blocked_intervals": []}
        return self.rescheduler.reschedule(current_plan, scheduling_event, context)

    def simulate_policy(
        self,
        policy_name: str,
        processes: List[Process],
        constraints: Any
    ) -> Any:
        """
        Runs Sandbox policy simulator.
        """
        policy = self.policy_manager.get_policy(policy_name)
        
        quantum_hours = constraints.get("quantum_hours", 2.0)
        available_hours = constraints.get("available_hours", 24.0)
        
        return self.simulator.simulate_policy(
            policy=policy,
            processes=processes,
            quantum_hours=quantum_hours,
            available_hours=available_hours,
            context=constraints
        )

    def validate_execution_plan(
        self,
        plan: ExecutionPlan,
        constraints: Any
    ) -> bool:
        """
        Invokes constraint engine to check hard failures on a plan.
        """
        violations = self.constraint_engine.validate_plan(plan, constraints)
        return len(violations) == 0

    def compute_metrics(
        self,
        processes: List[Process],
        last_slice_dates: Dict[str, datetime],
        history_stats: Dict[str, Dict[str, Any]]
    ) -> List[Process]:
        """
        Updates Attention Debt, Equity, and Health metrics for the provided processes.
        """
        updated_processes = []
        for p in processes:
            # 1. Attention Debt
            last_date = last_slice_dates.get(p.id)
            debt = self.debt_calc.calculate_debt(p, last_date)
            p.attention_debt = debt
            
            # 2. Attention Equity
            stats = history_stats.get(p.id, {"consecutive_completed": 0, "checklist_completion_rate": 0.0})
            equity = self.equity_calc.calculate_equity(
                consecutive_completed_slices=stats.get("consecutive_completed", 0),
                checklist_completion_rate=stats.get("checklist_completion_rate", 0.0)
            )
            p.attention_equity = equity
            
            # 3. Process Health
            p_deadline = p.deadline
            if p_deadline and p_deadline.tzinfo:
                p_deadline = p_deadline.astimezone(timezone.utc).replace(tzinfo=None)
            elif p_deadline:
                p_deadline = p_deadline.replace(tzinfo=None)
                
            now_naive = datetime.utcnow()
            time_left_hours = max(0.0, (p_deadline - now_naive).total_seconds() / 3600.0) if p_deadline else 0.0
            
            p.health_score = self.health_calc.calculate_health_score(p, time_left_hours)
            
            updated_processes.append(p)
            
        return updated_processes
