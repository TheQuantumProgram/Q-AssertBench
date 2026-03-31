from __future__ import annotations

from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


GOLD_SOURCE = """
allowed_outcomes = {"00", "11"}
ratio_00 = counts.get("00", 0) / shots
ratio_11 = counts.get("11", 0) / shots
unexpected_outcomes = sorted(set(counts) - allowed_outcomes)

assert not unexpected_outcomes, f"Unexpected outcomes detected: {unexpected_outcomes}"
assert counts.get("00", 0) > 0 and counts.get("11", 0) > 0, "Expected both Bell outcomes to appear"
assert abs(ratio_00 - ratio_11) < 0.1, "Bell-state outcomes are not balanced enough"
""".strip()


def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
    shots = result.shots
    allowed_outcomes = {"00", "11"}
    ratio_00 = result.counts.get("00", 0) / shots
    ratio_11 = result.counts.get("11", 0) / shots
    unexpected_outcomes = sorted(set(result.counts) - allowed_outcomes)

    try:
        assert not unexpected_outcomes, f"Unexpected outcomes detected: {unexpected_outcomes}"
        assert result.counts.get("00", 0) > 0 and result.counts.get("11", 0) > 0
        assert abs(ratio_00 - ratio_11) < 0.1
    except AssertionError as exc:
        return GoldAssertionResult(
            passed=False,
            details={
                "message": str(exc),
                "ratio_00": ratio_00,
                "ratio_11": ratio_11,
                "unexpected_outcomes": unexpected_outcomes,
                "counts": dict(result.counts),
            },
        )

    return GoldAssertionResult(
        passed=True,
        details={
            "ratio_00": ratio_00,
            "ratio_11": ratio_11,
            "unexpected_outcomes": unexpected_outcomes,
            "counts": dict(result.counts),
        },
    )
