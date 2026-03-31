from __future__ import annotations

from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


MIN_LEGAL_RATIO = 0.98
MIN_EVEN_STATES = 6

GOLD_SOURCE = """
legal_ratio = sum(
    count for state, count in counts.items() if state.count("1") % 2 == 0
) / shots
odd_outcomes = sorted(
    state for state, count in counts.items() if count > 0 and state.count("1") % 2 == 1
)
even_states = sorted(
    state for state, count in counts.items() if count > 0 and state.count("1") % 2 == 0
)

assert legal_ratio > 0.98, f"Expected almost all probability mass on even-parity states, but got {counts}"
assert not odd_outcomes, f"Observed odd-parity leakage: {odd_outcomes}"
assert len(even_states) >= 6, f"Expected broad even-parity support, but got {even_states}"
""".strip()


def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
    legal_ratio = sum(
        count for state, count in result.counts.items() if state.count("1") % 2 == 0
    ) / result.shots
    odd_outcomes = sorted(
        state
        for state, count in result.counts.items()
        if count > 0 and state.count("1") % 2 == 1
    )
    even_states = sorted(
        state
        for state, count in result.counts.items()
        if count > 0 and state.count("1") % 2 == 0
    )

    try:
        assert legal_ratio > MIN_LEGAL_RATIO
        assert not odd_outcomes
        assert len(even_states) >= MIN_EVEN_STATES
    except AssertionError as exc:
        return GoldAssertionResult(
            passed=False,
            details={
                "message": str(exc),
                "legal_ratio": legal_ratio,
                "odd_outcomes": odd_outcomes,
                "even_states": even_states,
                "counts": dict(result.counts),
            },
        )

    return GoldAssertionResult(
        passed=True,
        details={
            "legal_ratio": legal_ratio,
            "odd_outcomes": odd_outcomes,
            "even_states": even_states,
            "counts": dict(result.counts),
        },
    )
