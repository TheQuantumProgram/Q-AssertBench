"""Structured evaluation outcomes."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AlignmentResult:
    """Comparison result between a candidate and the benchmark gold assertion."""

    label: str
    score: float
    components: dict[str, object] = field(default_factory=dict)
    matched_terms: tuple[str, ...] = field(default_factory=tuple)
    missing_terms: tuple[str, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class TrialClassification:
    """Behavioral outcome plus alignment signal for one trial."""

    outcome: str
    failure_mode: str
    alignment_label: str
    failure_tags: tuple[str, ...]
    fault_detection_rate: float
