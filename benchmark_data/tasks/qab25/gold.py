from __future__ import annotations

from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


TARGET_STATES = {"101", "110"}
MIN_TARGET_RATIO = 0.95

GOLD_SOURCE = """
target_states = {"101", "110"}
target_ratio = sum(counts.get(state, 0) for state in target_states) / shots
unexpected_outcomes = sorted(set(counts) - target_states)

assert target_ratio > 0.95, f"Expected marked Grover states to dominate after diffusion, but got {counts}"
assert not unexpected_outcomes, f"Unexpected non-target outcomes detected: {unexpected_outcomes}"
assert counts.get("101", 0) > 0 and counts.get("110", 0) > 0, (
    "Expected both marked Grover states to appear after diffusion"
)
""".strip()


def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
    target_ratio = sum(result.counts.get(state, 0) for state in TARGET_STATES) / result.shots
    unexpected_outcomes = sorted(set(result.counts) - TARGET_STATES)

    try:
        assert target_ratio > MIN_TARGET_RATIO
        assert not unexpected_outcomes
        assert result.counts.get("101", 0) > 0 and result.counts.get("110", 0) > 0
    except AssertionError as exc:
        return GoldAssertionResult(
            passed=False,
            details={
                "message": str(exc),
                "target_ratio": target_ratio,
                "unexpected_outcomes": unexpected_outcomes,
                "counts": dict(result.counts),
            },
        )

    return GoldAssertionResult(
        passed=True,
        details={
            "target_ratio": target_ratio,
            "unexpected_outcomes": unexpected_outcomes,
            "counts": dict(result.counts),
        },
    )
