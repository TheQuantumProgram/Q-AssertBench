from __future__ import annotations

from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


EXPECTED_P1 = 0.5
TOLERANCE = 0.05

GOLD_SOURCE = """
p1 = counts.get("1", 0) / shots
tolerance = 0.05
assert abs(p1 - 0.5) < tolerance, (
    f"P(1) = {p1:.3f} does not match expected 0.500"
)
""".strip()


def _measure_one_probability(counts: dict[str, int], shots: int) -> float:
    return counts.get("1", 0) / shots


def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
    p1 = _measure_one_probability(result.counts, result.shots)

    try:
        assert abs(p1 - EXPECTED_P1) < TOLERANCE
    except AssertionError as exc:
        return GoldAssertionResult(
            passed=False,
            details={
                "message": str(exc),
                "p1": p1,
                "expected_p1": EXPECTED_P1,
                "tolerance": TOLERANCE,
                "counts": dict(result.counts),
            },
        )

    return GoldAssertionResult(
        passed=True,
        details={
            "p1": p1,
            "expected_p1": EXPECTED_P1,
            "tolerance": TOLERANCE,
            "counts": dict(result.counts),
        },
    )
