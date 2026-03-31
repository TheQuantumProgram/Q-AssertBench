from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from qasserbench.execution.interfaces import (
    ExecutionConfig,
    ExecutionResult,
    GoldAssertionResult,
    ProgramDefinition,
)
from qasserbench.execution.runtime import normalize_counts

SEARCH_QUBITS = 15
TARGET_BITSTRING = "101010101010101"


FAULT_TARGET_PROBABILITY = 0.08
FAULT_DISTRACTOR_PROBABILITIES = {
    "101010101010100": 0.12,
    "101010101010111": 0.10,
    "001010101010101": 0.08,
    "111010101010101": 0.07,
}


def _statevector_from_profile(
    *,
    target_probability: float,
    distractor_probabilities: dict[str, float],
) -> Statevector:
    dimension = 2**SEARCH_QUBITS
    probabilities = np.full(
        dimension,
        (1.0 - target_probability - sum(distractor_probabilities.values()))
        / (dimension - 1 - len(distractor_probabilities)),
        dtype=float,
    )
    probabilities[int(TARGET_BITSTRING, 2)] = target_probability
    for bitstring, probability in distractor_probabilities.items():
        probabilities[int(bitstring, 2)] = probability
    amplitudes = np.sqrt(probabilities.astype(complex))
    return Statevector(amplitudes)


def build_circuit() -> QuantumCircuit:
    circuit = QuantumCircuit(SEARCH_QUBITS, SEARCH_QUBITS)
    state = _statevector_from_profile(
        target_probability=FAULT_TARGET_PROBABILITY,
        distractor_probabilities=FAULT_DISTRACTOR_PROBABILITIES,
    )
    circuit.initialize(state.data, range(SEARCH_QUBITS))
    circuit.measure(range(SEARCH_QUBITS), range(SEARCH_QUBITS))
    return circuit


def build_program():
    return build_circuit()


def run_program(config: ExecutionConfig) -> ExecutionResult:
    state = _statevector_from_profile(
        target_probability=FAULT_TARGET_PROBABILITY,
        distractor_probabilities=FAULT_DISTRACTOR_PROBABILITIES,
    )
    if config.seed is not None:
        state.seed(config.seed)
    counts = normalize_counts(state.sample_counts(config.shots))
    metadata = dict(config.metadata)
    metadata.update(
        {
            "logical_qubits": SEARCH_QUBITS,
            "target_bitstring": TARGET_BITSTRING,
            "sampling_mode": "statevector_model",
            "fault": "weak_target_amplification",
        }
    )
    return ExecutionResult(
        counts=counts,
        shots=config.shots,
        backend=config.backend,
        metadata=metadata,
    )


def _placeholder_gold_assertion(_: ExecutionResult) -> GoldAssertionResult:
    return GoldAssertionResult(
        passed=False,
        details={"note": "Loader should replace this placeholder gold evaluator."},
    )


PROGRAM = ProgramDefinition(
    task_id="QAB31",
    build_program=build_program,
    run_program=run_program,
    evaluate_gold_assertion=_placeholder_gold_assertion,
)
