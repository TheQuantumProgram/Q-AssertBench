from __future__ import annotations

from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


MIN_FAMILY_RATIO = 0.98
MIN_LEGAL_STATES = 4
MAX_SINGLE_STATE_RATIO = 0.5

GOLD_SOURCE = """
legal_states = {state for state in counts if state.count("1") == 1}
family_ratio = sum(count for state, count in counts.items() if state.count("1") == 1) / shots
unexpected_outcomes = sorted(
    state for state, count in counts.items() if count > 0 and state.count("1") != 1
)
max_state_ratio = max(counts.values()) / shots if counts else 0.0

assert family_ratio > 0.98, f"Expected almost all probability mass on single-excitation states, but got {counts}"
assert not unexpected_outcomes, f"Observed leakage outside the single-excitation family: {unexpected_outcomes}"
assert len(legal_states) >= 4, f"Expected broad family support, but got {sorted(legal_states)}"
assert max_state_ratio < 0.5, f"Expected no single legal state to dominate, but got {counts}"
""".strip()


def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
    legal_states = {
        state for state, count in result.counts.items() if count > 0 and state.count("1") == 1
    }
    family_ratio = sum(
        count for state, count in result.counts.items() if state.count("1") == 1
    ) / result.shots
    unexpected_outcomes = sorted(
        state
        for state, count in result.counts.items()
        if count > 0 and state.count("1") != 1
    )
    max_state_ratio = max(result.counts.values()) / result.shots if result.counts else 0.0

    try:
        assert family_ratio > MIN_FAMILY_RATIO
        assert not unexpected_outcomes
        assert len(legal_states) >= MIN_LEGAL_STATES
        assert max_state_ratio < MAX_SINGLE_STATE_RATIO
    except AssertionError as exc:
        return GoldAssertionResult(
            passed=False,
            details={
                "message": str(exc),
                "family_ratio": family_ratio,
                "unexpected_outcomes": unexpected_outcomes,
                "legal_states": sorted(legal_states),
                "max_state_ratio": max_state_ratio,
                "counts": dict(result.counts),
            },
        )

    return GoldAssertionResult(
        passed=True,
        details={
            "family_ratio": family_ratio,
            "unexpected_outcomes": unexpected_outcomes,
            "legal_states": sorted(legal_states),
            "max_state_ratio": max_state_ratio,
            "counts": dict(result.counts),
        },
    )
