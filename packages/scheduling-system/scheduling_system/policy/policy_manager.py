from typing import Dict, List
from scheduling_system.interfaces.policy import ISchedulerPolicy
from .round_robin import RoundRobinPolicy
from .priority import PriorityPolicy

class PolicyManager:
    """
    Registry for managing available scheduling policies.
    Automatically registers default policies (Round Robin, Priority).
    """
    def __init__(self):
        self._policies: Dict[str, ISchedulerPolicy] = {}
        
        # Pre-register default policies
        self.register_policy(RoundRobinPolicy())
        self.register_policy(PriorityPolicy())

    def register_policy(self, policy: ISchedulerPolicy) -> None:
        """Registers a new scheduling policy."""
        self._policies[policy.name.lower()] = policy

    def get_policy(self, name: str) -> ISchedulerPolicy:
        """
        Retrieves a policy by its name (case-insensitive).
        Raises ValueError if the policy is not registered.
        """
        key = name.lower()
        if key not in self._policies:
            raise ValueError(f"Scheduling policy '{name}' is not registered.")
        return self._policies[key]

    def list_policies(self) -> List[str]:
        """Returns a list of names of all registered policies."""
        return [policy.name for policy in self._policies.values()]
