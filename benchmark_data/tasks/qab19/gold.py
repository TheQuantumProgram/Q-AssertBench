from __future__ import annotations

from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


EXPECTED_OUTCOMES = {"00", "11"}

GOLD_SOURCE = """
hidden_period = result.metadata.get("hidden_period", "11")
valid_outcomes = {"00", "11"}
invalid_outcomes = sorted(set(counts) - valid_outcomes)

assert hidden_period == "11", f"Unexpected hidden period metadata: {hidden_period}"
assert not invalid_outcomes, f"Invalid Simon samples found: {invalid_outcomes}"
assert counts.get("00", 0) > 0 and counts.get("11", 0) > 0, (
    f"Expected both valid Simon samples to appear, got {counts}"
)
""".strip()


def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
    hidden_period = str(result.metadata.get("hidden_period", "11"))
    invalid_outcomes = sorted(set(result.counts) - EXPECTED_OUTCOMES)

    try:
        assert hidden_period == "11"
        assert not invalid_outcomes
        assert result.counts.get("00", 0) > 0 and result.counts.get("11", 0) > 0
    except AssertionError as exc:
        return GoldAssertionResult(
            passed=False,
            details={
                "message": str(exc),
                "hidden_period": hidden_period,
                "invalid_outcomes": invalid_outcomes,
                "counts": dict(result.counts),
            },
        )

    return GoldAssertionResult(
        passed=True,
        details={
            "hidden_period": hidden_period,
            "invalid_outcomes": invalid_outcomes,
            "counts": dict(result.counts),
        },
    )
