from abc import ABC, abstractmethod
from typing import Any
from scheduling_system.models.time_slice import TimeSlice
from scheduling_system.models.execution_plan import ExecutionPlan

class IConstraint(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """The identifier name of the constraint."""
        pass

    @property
    @abstractmethod
    def is_hard(self) -> bool:
        """Returns True if this is a hard constraint (must be satisfied), False if soft (preference)."""
        pass

    @abstractmethod
    def validate_slice(self, time_slice: TimeSlice, context: Any) -> bool:
        """
        Validates if a specific TimeSlice satisfies this constraint.
        
        Args:
            time_slice: The TimeSlice to evaluate.
            context: Context containing calendar blockages, preferred working hours, etc.
            
        Returns:
            True if the slice is valid under this constraint, False otherwise.
        """
        pass

    @abstractmethod
    def validate_plan(self, plan: ExecutionPlan, context: Any) -> bool:
        """
        Validates if the entire ExecutionPlan satisfies this constraint.
        
        Args:
            plan: The entire ExecutionPlan to evaluate.
            context: Calendar and metadata context.
            
        Returns:
            True if the plan is valid, False otherwise.
        """
        pass
