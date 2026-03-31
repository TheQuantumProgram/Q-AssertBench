from __future__ import annotations

from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


TARGET_OUTCOME = "11"
MIN_TARGET_RATIO = 0.95

GOLD_SOURCE = """
target_ratio = counts.get("11", 0) / shots
other_ratio = sum(value for key, value in counts.items() if key != "11") / shots

assert target_ratio > 0.95, f"Expected the fixed balanced oracle to produce 11, but got {counts}"
assert other_ratio < 0.05, f"Unexpected extra outcomes detected: {counts}"
""".strip()


def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
    target_ratio = result.counts.get(TARGET_OUTCOME, 0) / result.shots
    other_ratio = sum(value for key, value in result.counts.items() if key != TARGET_OUTCOME) / result.shots

    try:
        assert target_ratio > MIN_TARGET_RATIO
        assert other_ratio < 1 - MIN_TARGET_RATIO
    except AssertionError as exc:
        return GoldAssertionResult(
            passed=False,
            details={
                "message": str(exc),
                "target_outcome": TARGET_OUTCOME,
                "target_ratio": target_ratio,
                "other_ratio": other_ratio,
                "counts": dict(result.counts),
            },
        )

    return GoldAssertionResult(
        passed=True,
        details={
            "target_outcome": TARGET_OUTCOME,
            "target_ratio": target_ratio,
            "other_ratio": other_ratio,
            "counts": dict(result.counts),
        },
    )
