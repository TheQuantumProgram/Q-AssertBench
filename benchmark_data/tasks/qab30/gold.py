from __future__ import annotations

from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


MIN_TOP_SIX_RATIO = 0.45
MAX_DOMINANT_RATIO = 0.75
MIN_SIGNIFICANT_STATES = 4
SIGNIFICANT_STATE_RATIO = 0.02

GOLD_SOURCE = """
sorted_counts = sorted(counts.items(), key=lambda item: item[1], reverse=True)
dominant_ratio = sorted_counts[0][1] / shots
top_six_ratio = sum(count for _, count in sorted_counts[:6]) / shots
significant_states = [state for state, count in counts.items() if count / shots >= 0.02]

assert top_six_ratio > 0.45, f"Expected several periodic peaks to dominate, but got top-six ratio={top_six_ratio:.3f}"
assert dominant_ratio < 0.75, f"Expected a multi-peak order-finding signature, but distribution collapsed to one state: {dominant_ratio:.3f}"
assert len(significant_states) >= 4, f"Expected at least four visible peaks, but got {significant_states}"
""".strip()


def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
    sorted_counts = sorted(result.counts.items(), key=lambda item: item[1], reverse=True)
    dominant_ratio = sorted_counts[0][1] / result.shots
    top_six_ratio = sum(count for _, count in sorted_counts[:6]) / result.shots
    significant_states = [
        state
        for state, count in result.counts.items()
        if count / result.shots >= SIGNIFICANT_STATE_RATIO
    ]

    try:
        assert top_six_ratio > MIN_TOP_SIX_RATIO
        assert dominant_ratio < MAX_DOMINANT_RATIO
        assert len(significant_states) >= MIN_SIGNIFICANT_STATES
    except AssertionError as exc:
        return GoldAssertionResult(
            passed=False,
            details={
                "message": str(exc),
                "dominant_ratio": dominant_ratio,
                "top_six_ratio": top_six_ratio,
                "significant_states": significant_states,
                "counts": dict(result.counts),
            },
        )

    return GoldAssertionResult(
        passed=True,
        details={
            "dominant_ratio": dominant_ratio,
            "top_six_ratio": top_six_ratio,
            "significant_states": significant_states,
            "counts": dict(result.counts),
        },
    )
