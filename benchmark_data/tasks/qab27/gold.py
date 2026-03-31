from __future__ import annotations

from fractions import Fraction

from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


EXPECTED_PEAKS = {"010", "110"}
EXPECTED_PERIOD = 4

GOLD_SOURCE = """
expected_peaks = {"010", "110"}
unexpected_outcomes = sorted(set(counts) - expected_peaks)
recovered_periods = {}

for state in expected_peaks:
    numerator = int(state, 2)
    recovered_periods[state] = Fraction(numerator, 2 ** 3).limit_denominator(15).denominator

assert not unexpected_outcomes, f"Unexpected non-peak outcomes detected: {unexpected_outcomes}"
for state, period in recovered_periods.items():
    assert period == 4, f"Expected continued fraction recovery of period 4 from {state}, got {period}"
""".strip()


def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
    unexpected_outcomes = sorted(set(result.counts) - EXPECTED_PEAKS)
    recovered_periods = {
        state: Fraction(int(state, 2), 2 ** 3).limit_denominator(15).denominator
        for state in sorted(EXPECTED_PEAKS)
    }

    try:
        assert not unexpected_outcomes
        for period in recovered_periods.values():
            assert period == EXPECTED_PERIOD
    except AssertionError as exc:
        return GoldAssertionResult(
            passed=False,
            details={
                "message": str(exc),
                "unexpected_outcomes": unexpected_outcomes,
                "recovered_periods": recovered_periods,
                "counts": dict(result.counts),
            },
        )

    return GoldAssertionResult(
        passed=True,
        details={
            "unexpected_outcomes": unexpected_outcomes,
            "recovered_periods": recovered_periods,
            "counts": dict(result.counts),
        },
    )
