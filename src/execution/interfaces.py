"""Shared execution interfaces for benchmark tasks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class ExecutionConfig:
    """Common configuration for benchmark program execution."""

    shots: int
    backend: str
    seed: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutionResult:
    """Normalized output of a program execution."""

    counts: dict[str, int]
    shots: int
    backend: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GoldAssertionResult:
    """Result returned by evaluating a benchmark gold assertion."""

    passed: bool
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AssertionCheckResult:
    """Result of executing a generated assertion candidate."""

    passed: bool
    error_type: str | None = None
    message: str | None = None


@dataclass(frozen=True)
class FaultCheckResult:
    """Assertion outcome for one fault-injected variant."""

    fault_id: str
    execution_result: ExecutionResult
    assertion_result: AssertionCheckResult


@dataclass(frozen=True)
class TrialExecutionRecord:
    """Nominal and fault-set execution evidence for one candidate."""

    nominal_execution: ExecutionResult
    nominal_assertion: AssertionCheckResult
    fault_results: list[FaultCheckResult] = field(default_factory=list)


@dataclass(frozen=True)
class ProgramDefinition:
    """Normalized benchmark program interface."""

    task_id: str
    build_program: Callable[[], Any]
    run_program: Callable[[ExecutionConfig], ExecutionResult]
    evaluate_gold_assertion: Callable[[ExecutionResult], GoldAssertionResult]
