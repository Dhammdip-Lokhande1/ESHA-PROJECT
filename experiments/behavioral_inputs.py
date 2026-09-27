"""
experiments/behavioral_inputs.py
============================================================
Behavioral input generator & execution tracker for EHSA experiments.
"""

from collections import defaultdict


class BehavioralExecutionTracker:
    def __init__(self):
        self.total_runs = 0
        self.success_runs = 0
        self.error_runs = 0
        self.timeouts = 0

    def record(self, output_str: str):
        self.total_runs += 1
        if output_str.startswith("ERROR: TimeoutExpired"):
            self.timeouts += 1
            self.error_runs += 1
        elif output_str.startswith("ERROR:"):
            self.error_runs += 1
        else:
            self.success_runs += 1

    def summary(self) -> dict:
        return {
            "total_executions": self.total_runs,
            "successful_executions": self.success_runs,
            "failed_executions": self.error_runs,
            "timeouts": self.timeouts,
            "success_rate": float(self.success_runs / self.total_runs) if self.total_runs > 0 else 0.0,
        }


# Standard sample stdin inputs for CodeNet Python problems
PROBLEM_INPUTS = {
    # Integers/Counts/Strings common stdin patterns
    "default": [
        "0\n",
        "1\n",
        "5\n",
        "10 20\n",
        "hello\n",
    ],
}


def get_behavioral_inputs_for_problem(problem_id: str | int) -> list[str]:
    pid_str = str(problem_id)
    if pid_str in PROBLEM_INPUTS:
        return PROBLEM_INPUTS[pid_str]
    return PROBLEM_INPUTS["default"]
