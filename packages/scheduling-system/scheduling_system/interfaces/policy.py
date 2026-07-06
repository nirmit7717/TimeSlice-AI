from abc import ABC, abstractmethod
from typing import List
from scheduling_system.models.process import Process
from scheduling_system.models.time_slice import TimeSlice

class ISchedulerPolicy(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the unique name identifier of the scheduling policy."""
        pass

    @abstractmethod
    def generate_slices(
        self, 
        processes: List[Process], 
        quantum_hours: float, 
        available_hours: float
    ) -> List[TimeSlice]:
        """
        Generates a scheduled list of time slices for the given processes.
        
        Args:
            processes: A list of Process domain models to schedule.
            quantum_hours: Time quantum size (slice duration limit) in hours.
            available_hours: Total available capacity time budget in hours.
            
        Returns:
            A list of generated TimeSlice records.
        """
        pass
