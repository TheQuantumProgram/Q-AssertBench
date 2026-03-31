from __future__ import annotations

from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


EXPECTED_SUPPORT = {"000", "010", "100", "110"}
MIN_PEAK_RATIO = 0.15

GOLD_SOURCE = """
expected_support = {"000", "010", "100", "110"}
invalid_outcomes = sorted(set(counts) - expected_support)
peak_ratios = {state: counts.get(state, 0) / shots for state in expected_support}

assert not invalid_outcomes, f"Unexpected non-peak outcomes detected: {invalid_outcomes}"
for state, ratio in peak_ratios.items():
    assert ratio > 0.15, f"Expected QFT peak at {state}, but observed ratio {ratio:.3f}"
""".strip()


def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
    invalid_outcomes = sorted(set(result.counts) - EXPECTED_SUPPORT)
    peak_ratios = {
        state: result.counts.get(state, 0) / result.shots
        for state in sorted(EXPECTED_SUPPORT)
    }

    try:
        assert not invalid_outcomes
        for ratio in peak_ratios.values():
            assert ratio > MIN_PEAK_RATIO
    except AssertionError as exc:
        return GoldAssertionResult(
            passed=False,
            details={
                "message": str(exc),
                "invalid_outcomes": invalid_outcomes,
                "peak_ratios": peak_ratios,
                "counts": dict(result.counts),
            },
        )

    return GoldAssertionResult(
        passed=True,
        details={
            "invalid_outcomes": invalid_outcomes,
            "peak_ratios": peak_ratios,
            "counts": dict(result.counts),
        },
    )
