class AttentionEquityCalculator:
    def calculate_equity(self, consecutive_completed_slices: int, checklist_completion_rate: float) -> float:
        """
        Calculates Attention Equity (momentum) from consistency and performance metrics.
        consecutive_completed_slices: Number of contiguous completed slices in the logs.
        checklist_completion_rate: Float between 0.0 and 1.0.
        """
        # Baseline equity increases with consistency and checklist fulfillment
        equity = (consecutive_completed_slices * 3.0) + (checklist_completion_rate * 10.0)
        
        # Bound between 0.0 and 100.0
        return round(min(100.0, max(0.0, equity)), 2)
