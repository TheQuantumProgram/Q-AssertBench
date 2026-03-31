from __future__ import annotations

from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


MIN_TARGET_RATIO = 0.95

GOLD_SOURCE = """
hidden_string = result.metadata.get("hidden_string", "111")
target_ratio = counts.get(hidden_string, 0) / shots
other_ratio = sum(value for key, value in counts.items() if key != hidden_string) / shots

assert target_ratio > 0.95, f"Expected hidden string {hidden_string}, but got {counts}"
assert other_ratio < 0.05, f"Unexpected extra outcomes detected: {counts}"
""".strip()


def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
    hidden_string = str(result.metadata.get("hidden_string", "111"))
    target_ratio = result.counts.get(hidden_string, 0) / result.shots
    other_ratio = sum(value for key, value in result.counts.items() if key != hidden_string) / result.shots

    try:
        assert target_ratio > MIN_TARGET_RATIO
        assert other_ratio < 1 - MIN_TARGET_RATIO
    except AssertionError as exc:
        return GoldAssertionResult(
            passed=False,
            details={
                "message": str(exc),
                "hidden_string": hidden_string,
                "target_ratio": target_ratio,
                "other_ratio": other_ratio,
                "counts": dict(result.counts),
            },
        )

    return GoldAssertionResult(
        passed=True,
        details={
            "hidden_string": hidden_string,
            "target_ratio": target_ratio,
            "other_ratio": other_ratio,
            "counts": dict(result.counts),
        },
    )
