from __future__ import annotations

from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


def xor_bitstrings(left: str, right: str) -> str:
    return "".join(str(int(left_bit) ^ int(right_bit)) for left_bit, right_bit in zip(left, right))


GOLD_SOURCE = """
hidden_period = result.metadata.get("hidden_period", "11")
num_input_qubits = result.metadata.get("num_input_qubits", 2)
branch_inputs = {}

for bitstring in counts:
    output_bits = bitstring[:-num_input_qubits]
    input_bits = bitstring[-num_input_qubits:]
    branch_inputs.setdefault(output_bits, set()).add(input_bits)

for output_bits, inputs in branch_inputs.items():
    assert len(inputs) == 2, f"Output branch {output_bits} did not collapse to exactly one Simon pair: {sorted(inputs)}"
    for input_bits in inputs:
        assert xor_bitstrings(input_bits, hidden_period) in inputs, (
            f"Input {input_bits} in branch {output_bits} is missing its Simon pair"
        )
""".strip()


def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
    hidden_period = str(result.metadata.get("hidden_period", "11"))
    num_input_qubits = int(result.metadata.get("num_input_qubits", 2))
    branch_inputs: dict[str, set[str]] = {}

    for bitstring in result.counts:
        output_bits = bitstring[:-num_input_qubits]
        input_bits = bitstring[-num_input_qubits:]
        branch_inputs.setdefault(output_bits, set()).add(input_bits)

    try:
        for output_bits, inputs in branch_inputs.items():
            assert len(inputs) == 2, (
                f"Output branch {output_bits} did not collapse to exactly one Simon pair: {sorted(inputs)}"
            )
            for input_bits in inputs:
                assert xor_bitstrings(input_bits, hidden_period) in inputs, (
                    f"Input {input_bits} in branch {output_bits} is missing its Simon pair"
                )
    except AssertionError as exc:
        return GoldAssertionResult(
            passed=False,
            details={
                "message": str(exc),
                "hidden_period": hidden_period,
                "branch_inputs": {key: sorted(value) for key, value in branch_inputs.items()},
                "counts": dict(result.counts),
            },
        )

    return GoldAssertionResult(
        passed=True,
        details={
            "hidden_period": hidden_period,
            "branch_inputs": {key: sorted(value) for key, value in branch_inputs.items()},
            "counts": dict(result.counts),
        },
    )
