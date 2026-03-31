from __future__ import annotations

from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


MIN_EXPECTED_RATIO = 0.95

GOLD_SOURCE = """
oracle_type = result.metadata.get("oracle_type", 0)
expected_state = "00" if oracle_type == 0 else "11"
expected_ratio = counts.get(expected_state, 0) / shots
other_ratio = sum(value for key, value in counts.items() if key != expected_state) / shots

assert oracle_type in {0, 1}, f"Unsupported oracle_type: {oracle_type}"
assert expected_ratio > 0.95, (
    f"Expected oracle_type {oracle_type} to produce input state {expected_state}, but got {counts}"
)
assert other_ratio < 0.05, f"Unexpected extra outcomes detected: {counts}"
""".strip()


def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
    oracle_type = int(result.metadata.get("oracle_type", 0))
    expected_state = "00" if oracle_type == 0 else "11"
    expected_ratio = result.counts.get(expected_state, 0) / result.shots
    other_ratio = sum(value for key, value in result.counts.items() if key != expected_state) / result.shots

    try:
        assert oracle_type in {0, 1}
        assert expected_ratio > MIN_EXPECTED_RATIO
        assert other_ratio < 1 - MIN_EXPECTED_RATIO
    except AssertionError as exc:
        return GoldAssertionResult(
            passed=False,
            details={
                "message": str(exc),
                "oracle_type": oracle_type,
                "expected_state": expected_state,
                "expected_ratio": expected_ratio,
                "other_ratio": other_ratio,
                "counts": dict(result.counts),
            },
        )

    return GoldAssertionResult(
        passed=True,
        details={
            "oracle_type": oracle_type,
            "expected_state": expected_state,
            "expected_ratio": expected_ratio,
            "other_ratio": other_ratio,
            "counts": dict(result.counts),
        },
    )
