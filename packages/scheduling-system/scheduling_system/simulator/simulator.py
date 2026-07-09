from datetime import timezone
from typing import List, Dict, Any
from scheduling_system.interfaces.policy import ISchedulerPolicy
from scheduling_system.models.process import Process
from scheduling_system.planner.execution_planner import ExecutionPlanner

class SchedulerSimulator:
    def __init__(self):
        self.planner = ExecutionPlanner()

    def simulate_policy(
        self,
        policy: ISchedulerPolicy,
        processes: List[Process],
        quantum_hours: float,
        available_hours: float,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Simulates running a policy on a set of workloads and constraints.
        Returns a dict of metrics evaluating policy performance.
        """
        # Generate plan in sandbox mode
        mock_plan = self.planner.plan(processes, policy, quantum_hours, available_hours, context)
        
        windows = mock_plan.execution_windows
        total_slices = len(windows)
        total_hours = sum(w.time_slice.duration_hours for w in windows)

        # 1. Context switches count
        context_switches = 0
        for i in range(len(windows) - 1):
            if windows[i].time_slice.process_id != windows[i+1].time_slice.process_id:
                context_switches += 1

        # 2. Neglected processes (got 0 hours in simulation)
        scheduled_proc_ids = {w.time_slice.process_id for w in windows}
        all_active_ids = {p.id for p in processes if p.remaining_effort_hours > 0}
        neglected_ids = all_active_ids - scheduled_proc_ids

        # 3. Deadline Misses
        deadline_misses = []
        process_map = {p.id: p for p in processes}
        for w in windows:
            ts = w.time_slice
            p = process_map.get(ts.process_id)
            if p:
                p_deadline = p.deadline
                if p_deadline.tzinfo is None:
                    p_deadline = p_deadline.replace(tzinfo=timezone.utc)
                ts_end = ts.end_time
                if ts_end.tzinfo is None:
                    ts_end = ts_end.replace(tzinfo=timezone.utc)

                if ts_end > p_deadline:
                    if p.id not in deadline_misses:
                        deadline_misses.append(p.id)

        is_feasible = len(deadline_misses) == 0 and len(all_active_ids) > 0

        return {
            "policy_name": policy.name,
            "is_feasible": is_feasible,
            "total_slices": total_slices,
            "total_scheduled_hours": round(total_hours, 2),
            "context_switches": context_switches,
            "neglected_processes_count": len(neglected_ids),
            "neglected_process_ids": list(neglected_ids),
            "deadline_misses_count": len(deadline_misses),
            "deadline_miss_ids": deadline_misses
        }
