from typing import Dict, Any
from scheduling_system.models.execution_plan import ExecutionPlan

class ImpactAnalyzer:
    def analyze_impact(self, original_plan: ExecutionPlan, updated_plan: ExecutionPlan) -> Dict[str, Any]:
        """
        Compares two execution plans and calculates displacement metrics and context switches.
        """
        orig_windows = original_plan.execution_windows
        upd_windows = updated_plan.execution_windows
        
        orig_map = {w.time_slice.id: w.time_slice for w in orig_windows}
        upd_map = {w.time_slice.id: w.time_slice for w in upd_windows}

        shifted_count = 0
        total_delay_hours = 0.0
        max_individual_delay = 0.0

        for slice_id, orig_slice in orig_map.items():
            if slice_id in upd_map:
                upd_slice = upd_map[slice_id]
                diff = (upd_slice.start_time - orig_slice.start_time).total_seconds() / 3600.0
                if abs(diff) > 0.01:  # Threshold for floating-point issues
                    shifted_count += 1
                    total_delay_hours += abs(diff)
                    if abs(diff) > max_individual_delay:
                        max_individual_delay = abs(diff)

        # Context switch count: switches between adjacent processes
        def count_context_switches(plan: ExecutionPlan) -> int:
            windows = plan.execution_windows
            if len(windows) <= 1:
                return 0
            switches = 0
            for i in range(len(windows) - 1):
                if windows[i].time_slice.process_id != windows[i+1].time_slice.process_id:
                    switches += 1
            return switches

        orig_switches = count_context_switches(original_plan)
        upd_switches = count_context_switches(updated_plan)

        return {
            "shifted_windows_count": shifted_count,
            "total_delay_hours": round(total_delay_hours, 2),
            "max_individual_delay_hours": round(max_individual_delay, 2),
            "context_switches_before": orig_switches,
            "context_switches_after": upd_switches,
            "context_switches_diff": upd_switches - orig_switches,
            "is_stable": shifted_count <= len(orig_windows) // 2  # Stable if less than half shifted
        }
