from datetime import datetime, timezone
from typing import List, Dict, Any, Set
from scheduling_system.models.process import Process, ProcessLifecycle

class ProcessAnalyzer:
    def validate_processes(self, processes: List[Process]) -> List[Process]:
        """
        Validates process parameters and filters out finished lifecycles (Completed/Archived).
        Raises ValueError for invalid values.
        """
        active_processes = []
        for p in processes:
            if p.estimated_effort_hours <= 0:
                raise ValueError(f"Process {p.id} has invalid estimated_effort_hours: must be > 0")
            if p.remaining_effort_hours < 0:
                raise ValueError(f"Process {p.id} has invalid remaining_effort_hours: must be >= 0")
            if p.remaining_effort_hours > p.estimated_effort_hours:
                raise ValueError(f"Process {p.id} remaining effort exceeds its total estimated effort")
            if not (1 <= p.priority <= 5):
                raise ValueError(f"Process {p.id} priority {p.priority} is out of bounds (1-5)")
            
            # Skip completed or archived processes since they don't need scheduling
            if p.status not in (ProcessLifecycle.COMPLETED, ProcessLifecycle.ARCHIVED):
                active_processes.append(p)
                
        return active_processes

    def estimate_total_workload(self, processes: List[Process], available_hours: float) -> Dict[str, Any]:
        """
        Computes summary metrics and identifies workload constraints and bottleneck processes.
        """
        active_procs = self.validate_processes(processes)
        if not active_procs:
            return {
                "total_remaining_hours": 0.0,
                "total_estimated_hours": 0.0,
                "total_attention_debt": 0.0,
                "average_priority": 0.0,
                "feasibility_ratio": 0.0,
                "bottlenecks": []
            }
            
        total_remaining = sum(p.remaining_effort_hours for p in active_procs)
        total_estimated = sum(p.estimated_effort_hours for p in active_procs)
        total_debt = sum(p.attention_debt for p in active_procs)
        avg_priority = sum(p.priority for p in active_procs) / len(active_procs)
        
        feasibility_ratio = total_remaining / available_hours if available_hours > 0 else float('inf')
        
        # Bottleneck detection: remaining effort exceeds capacity before deadline
        now = datetime.now(timezone.utc)
        bottlenecks = []
        for p in active_procs:
            # Ensure p.deadline has a timezone; if not, assume utc
            p_deadline = p.deadline
            if p_deadline.tzinfo is None:
                p_deadline = p_deadline.replace(tzinfo=timezone.utc)
                
            time_left_hours = (p_deadline - now).total_seconds() / 3600.0
            if time_left_hours < p.remaining_effort_hours:
                bottlenecks.append({
                    "process_id": p.id,
                    "name": p.name,
                    "remaining_hours": p.remaining_effort_hours,
                    "hours_until_deadline": max(0.0, time_left_hours),
                    "deficit_hours": p.remaining_effort_hours - max(0.0, time_left_hours)
                })
                
        return {
            "total_remaining_hours": total_remaining,
            "total_estimated_hours": total_estimated,
            "total_attention_debt": total_debt,
            "average_priority": round(avg_priority, 2),
            "feasibility_ratio": round(feasibility_ratio, 2),
            "bottlenecks": bottlenecks
        }

    def detect_dependencies(self, processes: List[Process]) -> Dict[str, List[str]]:
        """
        Maps processes to their dependency chains and flags circular references.
        Raises ValueError if a circular dependency is detected.
        """
        # Create adjacency list representation
        adj_list: Dict[str, List[str]] = {p.id: p.dependency_ids for p in processes}
        
        # DFS Cycle Detection
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        
        def has_cycle(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in adj_list.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
                    
            rec_stack.remove(node)
            return False
            
        for process_id in adj_list:
            if process_id not in visited:
                if has_cycle(process_id):
                    raise ValueError(f"Circular dependency detected in process path involving: {process_id}")
                    
        return adj_list

    def compute_scheduling_metadata(self, processes: List[Process]) -> List[Dict[str, Any]]:
        """
        Computes urgency and metrics metadata per process.
        """
        metadata = []
        now = datetime.now(timezone.utc)
        for p in processes:
            p_deadline = p.deadline
            if p_deadline.tzinfo is None:
                p_deadline = p_deadline.replace(tzinfo=timezone.utc)
                
            time_left_hours = (p_deadline - now).total_seconds() / 3600.0
            
            # Urgency score: higher priority, higher attention debt, shorter time left
            urgency_score = p.priority * 2.0 + p.attention_debt
            if time_left_hours > 0:
                urgency_score += (100.0 / time_left_hours)
            else:
                urgency_score += 1000.0  # Overdue is critical
                
            metadata.append({
                "process_id": p.id,
                "name": p.name,
                "time_left_hours": time_left_hours,
                "urgency_score": round(urgency_score, 2),
                "is_overdue": time_left_hours < 0
            })
            
        return sorted(metadata, key=lambda x: x["urgency_score"], reverse=True)
