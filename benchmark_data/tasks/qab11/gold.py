from __future__ import annotations

from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


MIN_BALANCED_RATIO = 0.95

GOLD_SOURCE = """
balanced_ratio = counts.get("1", 0) / shots
unexpected_states = sorted(set(counts) - {"0", "1"})

assert not unexpected_states, f"Unexpected decision-bit states: {unexpected_states}"
assert balanced_ratio > 0.95, f"Expected the balanced oracle to produce decision bit 1, but got {counts}"
""".strip()


def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
    balanced_ratio = result.counts.get("1", 0) / result.shots
    unexpected_states = sorted(set(result.counts) - {"0", "1"})

    try:
        assert not unexpected_states
        assert balanced_ratio > MIN_BALANCED_RATIO
    except AssertionError as exc:
        return GoldAssertionResult(
            passed=False,
            details={
                "message": str(exc),
                "balanced_ratio": balanced_ratio,
                "unexpected_states": unexpected_states,
                "counts": dict(result.counts),
            },
        )

    return GoldAssertionResult(
        passed=True,
        details={
            "balanced_ratio": balanced_ratio,
            "unexpected_states": unexpected_states,
            "counts": dict(result.counts),
        },
    )
