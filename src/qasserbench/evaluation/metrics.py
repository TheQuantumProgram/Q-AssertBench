"""Shared evaluation metrics."""

from __future__ import annotations

from qasserbench.execution.interfaces import TrialExecutionRecord


def fault_detection_rate(trial: TrialExecutionRecord) -> float:
    """Compute the fraction of fault variants caught by the candidate assertion."""

    if not trial.fault_results:
        return 0.0

    detections = sum(
        1
        for fault_result in trial.fault_results
        if not fault_result.assertion_result.passed
        and fault_result.assertion_result.error_type == "assertion_failed"
    )
    return detections / len(trial.fault_results)
