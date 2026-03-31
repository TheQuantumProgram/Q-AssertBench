from __future__ import annotations

from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


EXPECTED_OUTCOMES = {"000", "111"}
MAX_IMBALANCE = 0.1

GOLD_SOURCE = """
expected_outcomes = {"000", "111"}
unexpected_outcomes = sorted(set(counts) - expected_outcomes)
ratio_000 = counts.get("000", 0) / shots
ratio_111 = counts.get("111", 0) / shots

assert not unexpected_outcomes, f"Unexpected outcomes detected: {unexpected_outcomes}"
assert counts.get("000", 0) > 0 and counts.get("111", 0) > 0, (
    "Expected both correlated outcomes to appear"
)
assert abs(ratio_000 - ratio_111) < 0.1, "Correlated outcomes are too imbalanced"
""".strip()


def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
    unexpected_outcomes = sorted(set(result.counts) - EXPECTED_OUTCOMES)
    ratio_000 = result.counts.get("000", 0) / result.shots
    ratio_111 = result.counts.get("111", 0) / result.shots
    imbalance = abs(ratio_000 - ratio_111)

    try:
        assert not unexpected_outcomes, f"Unexpected outcomes detected: {unexpected_outcomes}"
        assert result.counts.get("000", 0) > 0 and result.counts.get("111", 0) > 0
        assert imbalance < MAX_IMBALANCE
    except AssertionError as exc:
        return GoldAssertionResult(
            passed=False,
            details={
                "message": str(exc),
                "unexpected_outcomes": unexpected_outcomes,
                "ratio_000": ratio_000,
                "ratio_111": ratio_111,
                "imbalance": imbalance,
                "max_imbalance": MAX_IMBALANCE,
                "counts": dict(result.counts),
            },
        )

    return GoldAssertionResult(
        passed=True,
        details={
            "unexpected_outcomes": unexpected_outcomes,
            "ratio_000": ratio_000,
            "ratio_111": ratio_111,
            "imbalance": imbalance,
            "max_imbalance": MAX_IMBALANCE,
            "counts": dict(result.counts),
        },
    )
