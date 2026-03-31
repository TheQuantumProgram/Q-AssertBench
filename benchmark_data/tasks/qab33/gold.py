from __future__ import annotations

from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


EXPECTED_SUM_BITS = "0111111"
EXPECTED_ADDEND_BITS = "100101"
MIN_DETERMINISTIC_RATIO = 0.95

GOLD_SOURCE = """
sorted_counts = sorted(counts.items(), key=lambda item: item[1], reverse=True)
top_state, top_count = sorted_counts[0]
deterministic_ratio = top_count / shots
sum_register_bits = top_state[:7]
restored_addend_bits = top_state[7:13]
carry_in_bit = top_state[13]

assert sum_register_bits == "0111111", f"Expected the ripple-carry adder to output sum bits 0111111, but got {sum_register_bits}"
assert restored_addend_bits == "100101", f"Expected the addend register to be restored to 100101, but got {restored_addend_bits}"
assert carry_in_bit == "0", f"Expected carry-in to remain cleared, but got {carry_in_bit}"
assert deterministic_ratio > 0.95, f"Expected a deterministic adder output, but got ratio={deterministic_ratio:.3f}"
""".strip()


def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
    sorted_counts = sorted(result.counts.items(), key=lambda item: item[1], reverse=True)
    top_state, top_count = sorted_counts[0]
    deterministic_ratio = top_count / result.shots
    sum_register_bits = top_state[:7]
    restored_addend_bits = top_state[7:13]
    carry_in_bit = top_state[13]

    try:
        assert sum_register_bits == EXPECTED_SUM_BITS
        assert restored_addend_bits == EXPECTED_ADDEND_BITS
        assert carry_in_bit == "0"
        assert deterministic_ratio > MIN_DETERMINISTIC_RATIO
    except AssertionError as exc:
        return GoldAssertionResult(
            passed=False,
            details={
                "message": str(exc),
                "top_state": top_state,
                "deterministic_ratio": deterministic_ratio,
                "sum_register_bits": sum_register_bits,
                "restored_addend_bits": restored_addend_bits,
                "carry_in_bit": carry_in_bit,
                "counts": dict(result.counts),
            },
        )

    return GoldAssertionResult(
        passed=True,
        details={
            "top_state": top_state,
            "deterministic_ratio": deterministic_ratio,
            "sum_register_bits": sum_register_bits,
            "restored_addend_bits": restored_addend_bits,
            "carry_in_bit": carry_in_bit,
            "counts": dict(result.counts),
        },
    )
