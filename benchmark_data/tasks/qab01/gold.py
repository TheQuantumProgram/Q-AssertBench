from __future__ import annotations

from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


GOLD_SOURCE = """
bit_occurrences = [set() for _ in range(len(next(iter(counts))))]
for bitstring in counts:
    for qubit_index, bit in enumerate(reversed(bitstring)):
        bit_occurrences[qubit_index].add(bit)

deterministic_qubits = [
    qubit_index for qubit_index, observed_bits in enumerate(bit_occurrences) if len(observed_bits) == 1
]
nondeterministic_qubits = [
    qubit_index for qubit_index, observed_bits in enumerate(bit_occurrences) if len(observed_bits) == 2
]

assert deterministic_qubits, "Expected at least one deterministic qubit"
assert nondeterministic_qubits, "Expected at least one non-deterministic qubit"
""".strip()


def _collect_bit_occurrences(counts: dict[str, int]) -> list[set[str]]:
    n_qubits = len(next(iter(counts)))
    bit_occurrences = [set() for _ in range(n_qubits)]
    for bitstring in counts:
        for qubit_index, bit in enumerate(reversed(bitstring)):
            bit_occurrences[qubit_index].add(bit)
    return bit_occurrences


def _classify_qubit_support(bit_occurrences: list[set[str]]) -> tuple[list[int], list[int]]:
    deterministic_qubits = [
        qubit_index for qubit_index, observed_bits in enumerate(bit_occurrences) if len(observed_bits) == 1
    ]
    nondeterministic_qubits = [
        qubit_index for qubit_index, observed_bits in enumerate(bit_occurrences) if len(observed_bits) == 2
    ]
    return deterministic_qubits, nondeterministic_qubits


def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
    bit_occurrences = _collect_bit_occurrences(result.counts)
    deterministic_qubits, nondeterministic_qubits = _classify_qubit_support(bit_occurrences)

    try:
        assert deterministic_qubits, "Expected at least one deterministic qubit"
        assert nondeterministic_qubits, "Expected at least one non-deterministic qubit"
    except AssertionError as exc:
        return GoldAssertionResult(
            passed=False,
            details={
                "message": str(exc),
                "bit_occurrences": [sorted(bits) for bits in bit_occurrences],
                "deterministic_qubits": deterministic_qubits,
                "nondeterministic_qubits": nondeterministic_qubits,
            },
        )

    return GoldAssertionResult(
        passed=True,
        details={
            "bit_occurrences": [sorted(bits) for bits in bit_occurrences],
            "deterministic_qubits": deterministic_qubits,
            "nondeterministic_qubits": nondeterministic_qubits,
        },
    )
