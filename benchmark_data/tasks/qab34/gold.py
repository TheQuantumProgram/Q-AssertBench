from __future__ import annotations

from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


GOOD_STATES = {"010101", "101010"}
MIN_GOOD_RATIO = 0.75
MIN_TOP_TWO_RATIO = 0.8

GOLD_SOURCE = """
good_states = {"010101", "101010"}
sorted_counts = sorted(counts.items(), key=lambda item: item[1], reverse=True)
top_state, _ = sorted_counts[0]
good_ratio = sum(counts.get(state, 0) for state in good_states) / shots
top_two_ratio = sum(count for _, count in sorted_counts[:2]) / shots

assert top_state in {"010101", "101010"}, f"Expected an optimal alternating cut assignment to dominate, but got {top_state}"
assert good_ratio > 0.75, f"Expected most probability mass on the optimal cut assignments, but got good_ratio={good_ratio:.3f}"
assert top_two_ratio > 0.8, f"Expected the two strongest peaks to dominate the layered QAOA output, but got top_two_ratio={top_two_ratio:.3f}"
""".strip()


def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
    sorted_counts = sorted(result.counts.items(), key=lambda item: item[1], reverse=True)
    top_state, _ = sorted_counts[0]
    good_ratio = sum(result.counts.get(state, 0) for state in GOOD_STATES) / result.shots
    top_two_ratio = sum(count for _, count in sorted_counts[:2]) / result.shots

    try:
        assert top_state in GOOD_STATES
        assert good_ratio > MIN_GOOD_RATIO
        assert top_two_ratio > MIN_TOP_TWO_RATIO
    except AssertionError as exc:
        return GoldAssertionResult(
            passed=False,
            details={
                "message": str(exc),
                "top_state": top_state,
                "good_ratio": good_ratio,
                "top_two_ratio": top_two_ratio,
                "counts": dict(result.counts),
            },
        )

    return GoldAssertionResult(
        passed=True,
        details={
            "top_state": top_state,
            "good_ratio": good_ratio,
            "top_two_ratio": top_two_ratio,
            "counts": dict(result.counts),
        },
    )
