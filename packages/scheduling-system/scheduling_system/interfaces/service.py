from abc import ABC, abstractmethod
from typing import List, Any
from scheduling_system.models.process import Process
from scheduling_system.models.execution_plan import ExecutionPlan

class ISchedulingService(ABC):
    @abstractmethod
    def generate_execution_plan(
        self,
        processes: List[Process],
        calendar: Any,
        preferences: Any,
        policy_name: str
    ) -> ExecutionPlan:
        """
        Creates a new validated Execution Plan using the designated policy and current calendar/preferences.
        """
        pass

    @abstractmethod
    def recompute_execution_plan(
        self,
        current_plan: ExecutionPlan,
        scheduling_event: Any
    ) -> ExecutionPlan:
        """
        Performs localized dynamic replanning in response to interrupts or events.
        """
        pass

    @abstractmethod
    def simulate_policy(
        self,
        policy_name: str,
        processes: List[Process],
        constraints: Any
    ) -> Any:
        """
        Runs a simulation to evaluate the workload feasibility under a specific policy.
        """
        pass

    @abstractmethod
    def validate_execution_plan(
        self,
        plan: ExecutionPlan,
        constraints: Any
    ) -> bool:
        """
        Ensures the plan satisfies all active hard constraints.
        """
        pass

    @abstractmethod
    def compute_metrics(
        self,
        execution_history: List[Any],
        process_history: List[Any]
    ) -> Any:
        """
        Triggers re-computation of core attention debt/equity/health metrics.
        """
        pass
