from __future__ import annotations

from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


MAX_DEVIATION = 0.08

GOLD_SOURCE = """
num_input_qubits = result.metadata.get("num_input_qubits", 3)
expected_probability = 1 / (2 ** num_input_qubits)

for state_index in range(2 ** num_input_qubits):
    state = format(state_index, f"0{num_input_qubits}b")
    probability = counts.get(state, 0) / shots
    assert abs(probability - expected_probability) < 0.08, (
        f"State {state} deviates too much from uniform superposition: {probability:.3f}"
    )
""".strip()


def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
    num_input_qubits = int(result.metadata.get("num_input_qubits", 3))
    expected_probability = 1 / (2 ** num_input_qubits)
    probabilities: dict[str, float] = {}

    try:
        for state_index in range(2 ** num_input_qubits):
            state = format(state_index, f"0{num_input_qubits}b")
            probability = result.counts.get(state, 0) / result.shots
            probabilities[state] = probability
            assert abs(probability - expected_probability) < MAX_DEVIATION
    except AssertionError as exc:
        return GoldAssertionResult(
            passed=False,
            details={
                "message": str(exc),
                "expected_probability": expected_probability,
                "max_deviation": MAX_DEVIATION,
                "probabilities": probabilities,
                "counts": dict(result.counts),
            },
        )

    return GoldAssertionResult(
        passed=True,
        details={
            "expected_probability": expected_probability,
            "max_deviation": MAX_DEVIATION,
            "probabilities": probabilities,
            "counts": dict(result.counts),
        },
    )
