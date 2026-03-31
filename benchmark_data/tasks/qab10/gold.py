from __future__ import annotations

from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


EXPECTED_OUTCOMES = {"0000", "1111"}
MIN_VALID_RATIO = 0.95
MAX_IMBALANCE = 0.15

GOLD_SOURCE = """
valid_ratio = sum(value for key, value in counts.items() if key in {"0000", "1111"}) / shots
ratio_0000 = counts.get("0000", 0) / shots
ratio_1111 = counts.get("1111", 0) / shots
unexpected_outcomes = sorted(set(counts) - {"0000", "1111"})

assert valid_ratio > 0.95, f"Unexpected states found: {counts}"
assert counts.get("0000", 0) > 0 and counts.get("1111", 0) > 0, (
    "Expected both GHZ outcomes to appear"
)
assert abs(ratio_0000 - ratio_1111) < 0.15, "GHZ outcomes are too imbalanced"
""".strip()


def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
    valid_ratio = sum(
        value for key, value in result.counts.items() if key in EXPECTED_OUTCOMES
    ) / result.shots
    ratio_0000 = result.counts.get("0000", 0) / result.shots
    ratio_1111 = result.counts.get("1111", 0) / result.shots
    imbalance = abs(ratio_0000 - ratio_1111)
    unexpected_outcomes = sorted(set(result.counts) - EXPECTED_OUTCOMES)

    try:
        assert valid_ratio > MIN_VALID_RATIO
        assert result.counts.get("0000", 0) > 0 and result.counts.get("1111", 0) > 0
        assert imbalance < MAX_IMBALANCE
    except AssertionError as exc:
        return GoldAssertionResult(
            passed=False,
            details={
                "message": str(exc),
                "valid_ratio": valid_ratio,
                "ratio_0000": ratio_0000,
                "ratio_1111": ratio_1111,
                "imbalance": imbalance,
                "unexpected_outcomes": unexpected_outcomes,
                "counts": dict(result.counts),
            },
        )

    return GoldAssertionResult(
        passed=True,
        details={
            "valid_ratio": valid_ratio,
            "ratio_0000": ratio_0000,
            "ratio_1111": ratio_1111,
            "imbalance": imbalance,
            "unexpected_outcomes": unexpected_outcomes,
            "counts": dict(result.counts),
        },
    )
