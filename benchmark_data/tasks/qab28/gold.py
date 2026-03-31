from __future__ import annotations

from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


MIN_DOMINANT_RATIO = 0.6

GOLD_SOURCE = """
dominant_state = result.metadata.get("dominant_state", "000")
dominant_ratio = counts.get(dominant_state, 0) / shots

assert dominant_ratio > 0.6, (
    f"Expected dominant HHL solution state {dominant_state}, but got ratio {dominant_ratio:.3f} from {counts}"
)
""".strip()


def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
    dominant_state = str(result.metadata.get("dominant_state", "000"))
    dominant_ratio = result.counts.get(dominant_state, 0) / result.shots

    try:
        assert dominant_ratio > MIN_DOMINANT_RATIO
    except AssertionError as exc:
        return GoldAssertionResult(
            passed=False,
            details={
                "message": str(exc),
                "dominant_state": dominant_state,
                "dominant_ratio": dominant_ratio,
                "counts": dict(result.counts),
            },
        )

    return GoldAssertionResult(
        passed=True,
        details={
            "dominant_state": dominant_state,
            "dominant_ratio": dominant_ratio,
            "counts": dict(result.counts),
        },
    )
