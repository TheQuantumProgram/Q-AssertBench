from __future__ import annotations

from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


EXPECTED_PROB_Q0 = 0.7

GOLD_SOURCE = """
tolerance = 0.1
q0_one_counts = sum(count for bitstring, count in counts.items() if bitstring[-1] == "1")
q0_one_ratio = q0_one_counts / shots
assert abs(q0_one_ratio - 0.7) < tolerance, (
    f"q0 measurement ratio {q0_one_ratio:.3f} does not match expected 0.700"
)
""".strip()


def _measure_q0_one_ratio(counts: dict[str, int], shots: int) -> float:
    q0_one_counts = sum(
        count for bitstring, count in counts.items() if bitstring[-1] == "1"
    )
    return q0_one_counts / shots


def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
    tolerance = 0.1
    q0_one_ratio = _measure_q0_one_ratio(result.counts, result.shots)

    try:
        assert abs(q0_one_ratio - EXPECTED_PROB_Q0) < tolerance
    except AssertionError as exc:
        return GoldAssertionResult(
            passed=False,
            details={
                "message": str(exc),
                "q0_one_ratio": q0_one_ratio,
                "expected_q0_one_ratio": EXPECTED_PROB_Q0,
                "tolerance": tolerance,
            },
        )

    return GoldAssertionResult(
        passed=True,
        details={
            "q0_one_ratio": q0_one_ratio,
            "expected_q0_one_ratio": EXPECTED_PROB_Q0,
            "tolerance": tolerance,
        },
    )
