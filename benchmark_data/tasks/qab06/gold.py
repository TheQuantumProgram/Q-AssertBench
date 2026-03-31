from __future__ import annotations

from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


EXPECTED_DOMINANT_STATE = "1101"
MIN_DOMINANT_RATIO = 0.85

GOLD_SOURCE = """
dominant_state = max(counts, key=counts.get)
dominant_ratio = counts[dominant_state] / shots
assert dominant_state == "1101", f"Expected dominant state 1101, got {dominant_state}"
assert dominant_ratio > 0.85, (
    f"Dominant-state ratio {dominant_ratio:.3f} is lower than expected"
)
""".strip()


def _measure_dominance(counts: dict[str, int], shots: int) -> tuple[str, float]:
    dominant_state = max(counts, key=counts.get)
    dominant_ratio = counts[dominant_state] / shots
    return dominant_state, dominant_ratio


def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
    dominant_state, dominant_ratio = _measure_dominance(result.counts, result.shots)

    try:
        assert dominant_state == EXPECTED_DOMINANT_STATE
        assert dominant_ratio > MIN_DOMINANT_RATIO
    except AssertionError as exc:
        return GoldAssertionResult(
            passed=False,
            details={
                "message": str(exc),
                "dominant_state": dominant_state,
                "expected_dominant_state": EXPECTED_DOMINANT_STATE,
                "dominant_ratio": dominant_ratio,
                "min_dominant_ratio": MIN_DOMINANT_RATIO,
                "counts": dict(result.counts),
            },
        )

    return GoldAssertionResult(
        passed=True,
        details={
            "dominant_state": dominant_state,
            "expected_dominant_state": EXPECTED_DOMINANT_STATE,
            "dominant_ratio": dominant_ratio,
            "min_dominant_ratio": MIN_DOMINANT_RATIO,
            "counts": dict(result.counts),
        },
    )
