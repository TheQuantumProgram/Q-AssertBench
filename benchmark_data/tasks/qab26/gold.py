from __future__ import annotations

from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


EXPECTED_PEAKS = {"00000", "00010", "00100", "00110"}
MIN_PEAK_RATIO = 0.18
MAX_PEAK_RATIO = 0.32

GOLD_SOURCE = """
expected_peaks = {"00000", "00010", "00100", "00110"}
invalid_outcomes = sorted(set(counts) - expected_peaks)
peak_ratios = {state: counts.get(state, 0) / shots for state in expected_peaks}

assert not invalid_outcomes, f"Unexpected non-periodic outcomes detected: {invalid_outcomes}"
for state, ratio in peak_ratios.items():
    assert 0.18 < ratio < 0.32, (
        f"Expected balanced period peak at {state}, but observed ratio {ratio:.3f}"
    )
""".strip()


def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
    invalid_outcomes = sorted(set(result.counts) - EXPECTED_PEAKS)
    peak_ratios = {
        state: result.counts.get(state, 0) / result.shots
        for state in sorted(EXPECTED_PEAKS)
    }

    try:
        assert not invalid_outcomes
        for ratio in peak_ratios.values():
            assert MIN_PEAK_RATIO < ratio < MAX_PEAK_RATIO
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
