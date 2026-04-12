"""Behavioral outcome classification."""

from __future__ import annotations

from qasserbench.evaluation.metrics import fault_detection_rate
from qasserbench.evaluation.outcomes import AlignmentResult, TrialClassification
from qasserbench.execution.interfaces import TrialExecutionRecord
from qasserbench.generation.artifacts import CandidateAssertionArtifact


def classify_trial(
    artifact: CandidateAssertionArtifact,
    trial: TrialExecutionRecord,
    alignment: AlignmentResult,
) -> TrialClassification:
    """Classify one candidate trial behaviorally and attach alignment tags."""

    tags: list[str] = []
    rate = fault_detection_rate(trial)

    if not artifact.is_usable:
        if "empty_response" in artifact.diagnostics:
            outcome = "generation_failure"
            failure_mode = "generation_failure"
        else:
            outcome = "format_error"
            failure_mode = "format_error"
    elif trial.nominal_assertion.error_type == "runtime_error":
        outcome = "invalid"
        failure_mode = "invalid"
        tags.append("runtime_error")
    elif not trial.nominal_assertion.passed:
        outcome = "misjudge"
        failure_mode = "nominal_failure"
        tags.append("nominal_failure")
    elif trial.fault_results and rate < 1.0:
        outcome = "misjudge"
        failure_mode = "fault_side_failure"
        tags.append("fault_insensitive")
    else:
        outcome = "pass"
        failure_mode = "none"

    if alignment.label == "misaligned":
        tags.append("gold_misalignment")
    elif alignment.label == "not_assessable":
        tags.append("alignment_not_assessable")

    return TrialClassification(
        outcome=outcome,
        failure_mode=failure_mode,
        alignment_label=alignment.label,
        failure_tags=tuple(tags),
        fault_detection_rate=rate,
    )
