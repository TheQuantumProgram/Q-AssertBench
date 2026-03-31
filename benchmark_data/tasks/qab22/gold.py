from __future__ import annotations

from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


MIN_EXPECTED_RATIO = 0.95

GOLD_SOURCE = """
expected_state = result.metadata.get("expected_state", "101")
expected_ratio = counts.get(expected_state, 0) / shots
other_ratio = sum(value for key, value in counts.items() if key != expected_state) / shots

assert expected_ratio > 0.95, f"Expected {expected_state} to be recovered, but got {counts}"
assert other_ratio < 0.05, f"Unexpected extra outcomes detected: {counts}"
""".strip()


def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
    expected_state = str(result.metadata.get("expected_state", "101"))
    expected_ratio = result.counts.get(expected_state, 0) / result.shots
    other_ratio = sum(value for key, value in result.counts.items() if key != expected_state) / result.shots

    try:
        assert expected_ratio > MIN_EXPECTED_RATIO
        assert other_ratio < 1 - MIN_EXPECTED_RATIO
    except AssertionError as exc:
        return GoldAssertionResult(
            passed=False,
            details={
                "message": str(exc),
                "expected_state": expected_state,
                "expected_ratio": expected_ratio,
                "other_ratio": other_ratio,
                "counts": dict(result.counts),
            },
        )

    return GoldAssertionResult(
        passed=True,
        details={
            "expected_state": expected_state,
            "expected_ratio": expected_ratio,
            "other_ratio": other_ratio,
            "counts": dict(result.counts),
        },
    )
