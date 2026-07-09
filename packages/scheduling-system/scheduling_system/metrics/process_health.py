from datetime import datetime, timezone
from scheduling_system.models.process import Process

class ProcessHealthCalculator:
    def calculate_health_score(self, process: Process, time_left_hours: float) -> float:
        """
        Computes overall Process Health on a 0-100 scale based on:
        - Attention Debt (neglect)
        - Attention Equity (momentum)
        - Deadline Risk (remaining effort vs time left)
        """
        score = 100.0

        # 1. Penalty for Attention Debt
        debt_penalty = min(35.0, process.attention_debt * 2.5)
        score -= debt_penalty

        # 2. Bonus for Attention Equity
        equity_bonus = min(15.0, process.attention_equity * 0.20)
        score += equity_bonus

        # 3. Penalty for Deadline Risk
        if time_left_hours > 0:
            if time_left_hours < process.remaining_effort_hours:
                # Deficit exists: remaining effort exceeds hours left
                deficit = process.remaining_effort_hours - time_left_hours
                deadline_penalty = min(50.0, (deficit / max(1.0, process.remaining_effort_hours)) * 50.0)
                score -= deadline_penalty
        else:
            # Overdue is critical
            score -= 60.0

        return round(min(100.0, max(0.0, score)), 2)

    def get_health_status(self, score: float) -> str:
        """
        Maps numerical health score to standard category.
        """
        if score >= 90.0:
            return "Excellent"
        elif score >= 75.0:
            return "Good"
        elif score >= 60.0:
            return "Fair"
        elif score >= 40.0:
            return "Needs Attention"
        else:
            return "Critical"
