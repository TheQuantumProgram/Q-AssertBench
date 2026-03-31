from __future__ import annotations

from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


EXPECTED_OUTCOMES = {"00", "11"}
MIN_CORRELATED_RATIO = 0.95
MAX_IMBALANCE = 0.15

GOLD_SOURCE = """
correlated_ratio = sum(value for key, value in counts.items() if key in {"00", "11"}) / shots
ratio_00 = counts.get("00", 0) / shots
ratio_11 = counts.get("11", 0) / shots
unexpected_outcomes = sorted(set(counts) - {"00", "11"})

assert correlated_ratio > 0.95, f"Expected almost all outcomes to be 00 or 11, but got {counts}"
assert counts.get("00", 0) > 0 and counts.get("11", 0) > 0, (
    "Expected both correlated outcomes 00 and 11 to appear"
)
assert abs(ratio_00 - ratio_11) < 0.15, "Correlated outcomes are too imbalanced"
""".strip()


def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
    correlated_ratio = sum(
        value for key, value in result.counts.items() if key in EXPECTED_OUTCOMES
    ) / result.shots
    ratio_00 = result.counts.get("00", 0) / result.shots
    ratio_11 = result.counts.get("11", 0) / result.shots
    imbalance = abs(ratio_00 - ratio_11)
    unexpected_outcomes = sorted(set(result.counts) - EXPECTED_OUTCOMES)

    try:
        assert correlated_ratio > MIN_CORRELATED_RATIO
        assert result.counts.get("00", 0) > 0 and result.counts.get("11", 0) > 0
        assert imbalance < MAX_IMBALANCE
    except AssertionError as exc:
        return GoldAssertionResult(
            passed=False,
            details={
                "message": str(exc),
                "correlated_ratio": correlated_ratio,
                "ratio_00": ratio_00,
                "ratio_11": ratio_11,
                "imbalance": imbalance,
                "unexpected_outcomes": unexpected_outcomes,
                "counts": dict(result.counts),
            },
        )

    return GoldAssertionResult(
        passed=True,
        details={
            "correlated_ratio": correlated_ratio,
            "ratio_00": ratio_00,
            "ratio_11": ratio_11,
            "imbalance": imbalance,
            "unexpected_outcomes": unexpected_outcomes,
            "counts": dict(result.counts),
        },
    )
