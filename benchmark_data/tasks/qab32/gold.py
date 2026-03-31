from __future__ import annotations

from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


COUNTING_QUBITS = 6
EXPECTED_PHASE_BITSTRING = "101011"
MIN_TARGET_RATIO = 0.9
MIN_NEARBY_RATIO = 0.95

GOLD_SOURCE = """
sorted_counts = sorted(counts.items(), key=lambda item: item[1], reverse=True)
top_state, _ = sorted_counts[0]
target_ratio = counts.get("101011", 0) / shots
expected_index = int("101011", 2)
nearby_states = [format((expected_index + delta) % (2**COUNTING_QUBITS), f"0{COUNTING_QUBITS}b") for delta in (-1, 0, 1)]
nearby_ratio = sum(counts.get(state, 0) for state in nearby_states) / shots

assert top_state == "101011", f"Expected the dominant QPE estimate to be 101011, but got {top_state}"
assert target_ratio > 0.9, f"Expected the target phase estimate to dominate, but got ratio={target_ratio:.3f}"
assert nearby_ratio > 0.95, f"Expected almost all probability mass near the target phase estimate, but got nearby_ratio={nearby_ratio:.3f}"
""".strip()


def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
    sorted_counts = sorted(result.counts.items(), key=lambda item: item[1], reverse=True)
    top_state, _ = sorted_counts[0]
    target_ratio = result.counts.get(EXPECTED_PHASE_BITSTRING, 0) / result.shots
    expected_index = int(EXPECTED_PHASE_BITSTRING, 2)
    nearby_states = [
        format((expected_index + delta) % (2**COUNTING_QUBITS), f"0{COUNTING_QUBITS}b")
        for delta in (-1, 0, 1)
    ]
    nearby_ratio = sum(result.counts.get(state, 0) for state in nearby_states) / result.shots

    try:
        assert top_state == EXPECTED_PHASE_BITSTRING
        assert target_ratio > MIN_TARGET_RATIO
        assert nearby_ratio > MIN_NEARBY_RATIO
    except AssertionError as exc:
        return GoldAssertionResult(
            passed=False,
            details={
                "message": str(exc),
                "top_state": top_state,
                "target_ratio": target_ratio,
                "nearby_ratio": nearby_ratio,
                "counts": dict(result.counts),
            },
        )

    return GoldAssertionResult(
        passed=True,
        details={
            "top_state": top_state,
            "target_ratio": target_ratio,
            "nearby_ratio": nearby_ratio,
            "counts": dict(result.counts),
        },
    )
