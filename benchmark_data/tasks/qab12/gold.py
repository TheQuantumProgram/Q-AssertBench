from __future__ import annotations

from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


MIN_DECISION_RATIO = 0.95

GOLD_SOURCE = """
oracle_type = result.metadata.get("oracle_type", 0)
zero_ratio = counts.get("0", 0) / shots
one_ratio = counts.get("1", 0) / shots
expected_state = "0" if oracle_type == 0 else "1"
expected_ratio = zero_ratio if expected_state == "0" else one_ratio

assert oracle_type in {0, 1}, f"Unsupported oracle_type: {oracle_type}"
assert expected_ratio > 0.95, (
    f"Expected oracle_type {oracle_type} to produce decision bit {expected_state}, but got {counts}"
)
""".strip()


def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
    oracle_type = int(result.metadata.get("oracle_type", 0))
    zero_ratio = result.counts.get("0", 0) / result.shots
    one_ratio = result.counts.get("1", 0) / result.shots
    expected_state = "0" if oracle_type == 0 else "1"
    expected_ratio = zero_ratio if expected_state == "0" else one_ratio

    try:
        assert oracle_type in {0, 1}
        assert expected_ratio > MIN_DECISION_RATIO
    except AssertionError as exc:
        return GoldAssertionResult(
            passed=False,
            details={
                "message": str(exc),
                "oracle_type": oracle_type,
                "expected_state": expected_state,
                "zero_ratio": zero_ratio,
                "one_ratio": one_ratio,
                "counts": dict(result.counts),
            },
        )

    return GoldAssertionResult(
        passed=True,
        details={
            "oracle_type": oracle_type,
            "expected_state": expected_state,
            "zero_ratio": zero_ratio,
            "one_ratio": one_ratio,
            "counts": dict(result.counts),
        },
    )
