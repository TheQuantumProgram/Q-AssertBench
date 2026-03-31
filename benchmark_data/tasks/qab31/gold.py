from __future__ import annotations

from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


TARGET_BITSTRING = "101010101010101"
MIN_TARGET_RATIO = 0.25
MIN_AMPLIFICATION_GAP = 2.0

GOLD_SOURCE = """
sorted_counts = sorted(counts.items(), key=lambda item: item[1], reverse=True)
top_state, top_count = sorted_counts[0]
target_count = counts.get("101010101010101", 0)
target_prob = target_count / shots
second_best_prob = max(
    (count / shots for state, count in sorted_counts if state != "101010101010101"),
    default=0.0,
)

assert top_state == "101010101010101", f"Expected the Grover target to be the most frequent state, but got {top_state}"
assert target_prob > 0.25, f"Expected clear target amplification, but got target_prob={target_prob:.3f}"
assert target_prob > second_best_prob * 2.0, (
    f"Expected the target to stand out from distractors, but got target={target_prob:.3f}, second={second_best_prob:.3f}"
)
""".strip()


def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
    sorted_counts = sorted(result.counts.items(), key=lambda item: item[1], reverse=True)
    top_state, _ = sorted_counts[0]
    target_count = result.counts.get(TARGET_BITSTRING, 0)
    target_prob = target_count / result.shots
    second_best_prob = max(
        (
            count / result.shots
            for state, count in sorted_counts
            if state != TARGET_BITSTRING
        ),
        default=0.0,
    )

    try:
        assert top_state == TARGET_BITSTRING
        assert target_prob > MIN_TARGET_RATIO
        assert target_prob > second_best_prob * MIN_AMPLIFICATION_GAP
    except AssertionError as exc:
        return GoldAssertionResult(
            passed=False,
            details={
                "message": str(exc),
                "top_state": top_state,
                "target_prob": target_prob,
                "second_best_prob": second_best_prob,
                "counts": dict(result.counts),
            },
        )

    return GoldAssertionResult(
        passed=True,
        details={
            "top_state": top_state,
            "target_prob": target_prob,
            "second_best_prob": second_best_prob,
            "counts": dict(result.counts),
        },
    )
