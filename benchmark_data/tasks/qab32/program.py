from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit, transpile

from qasserbench.execution.backends import get_backend
from qasserbench.execution.interfaces import (
    ExecutionConfig,
    ExecutionResult,
    GoldAssertionResult,
    ProgramDefinition,
)
from qasserbench.execution.runtime import normalize_counts


COUNTING_QUBITS = 6
TOTAL_QUBITS = COUNTING_QUBITS + 1
PHASE_NUMERATOR = 43
PHASE_DENOMINATOR = 2**COUNTING_QUBITS
EXPECTED_PHASE_BITSTRING = format(PHASE_NUMERATOR, f"0{COUNTING_QUBITS}b")


def build_circuit(*, include_highest_frequency_layer: bool = True) -> QuantumCircuit:
    circuit = QuantumCircuit(TOTAL_QUBITS, COUNTING_QUBITS)
    eigen_qubit = COUNTING_QUBITS
    base_angle = 2 * np.pi * PHASE_NUMERATOR / PHASE_DENOMINATOR

    circuit.x(eigen_qubit)

    circuit.h(0)
    circuit.h(1)
    circuit.h(2)
    circuit.h(3)
    circuit.h(4)
    circuit.h(5)

    circuit.barrier()

    circuit.cp(base_angle, 0, eigen_qubit)

    circuit.cp(base_angle, 1, eigen_qubit)
    circuit.cp(base_angle, 1, eigen_qubit)

    circuit.cp(base_angle, 2, eigen_qubit)
    circuit.cp(base_angle, 2, eigen_qubit)
    circuit.cp(base_angle, 2, eigen_qubit)
    circuit.cp(base_angle, 2, eigen_qubit)

    circuit.cp(base_angle, 3, eigen_qubit)
    circuit.cp(base_angle, 3, eigen_qubit)
    circuit.cp(base_angle, 3, eigen_qubit)
    circuit.cp(base_angle, 3, eigen_qubit)
    circuit.cp(base_angle, 3, eigen_qubit)
    circuit.cp(base_angle, 3, eigen_qubit)
    circuit.cp(base_angle, 3, eigen_qubit)
    circuit.cp(base_angle, 3, eigen_qubit)

    circuit.cp(base_angle, 4, eigen_qubit)
    circuit.cp(base_angle, 4, eigen_qubit)
    circuit.cp(base_angle, 4, eigen_qubit)
    circuit.cp(base_angle, 4, eigen_qubit)
    circuit.cp(base_angle, 4, eigen_qubit)
    circuit.cp(base_angle, 4, eigen_qubit)
    circuit.cp(base_angle, 4, eigen_qubit)
    circuit.cp(base_angle, 4, eigen_qubit)
    circuit.cp(base_angle, 4, eigen_qubit)
    circuit.cp(base_angle, 4, eigen_qubit)
    circuit.cp(base_angle, 4, eigen_qubit)
    circuit.cp(base_angle, 4, eigen_qubit)
    circuit.cp(base_angle, 4, eigen_qubit)
    circuit.cp(base_angle, 4, eigen_qubit)
    circuit.cp(base_angle, 4, eigen_qubit)
    circuit.cp(base_angle, 4, eigen_qubit)

    if include_highest_frequency_layer:
        circuit.cp(base_angle, 5, eigen_qubit)
        circuit.cp(base_angle, 5, eigen_qubit)
        circuit.cp(base_angle, 5, eigen_qubit)
        circuit.cp(base_angle, 5, eigen_qubit)
        circuit.cp(base_angle, 5, eigen_qubit)
        circuit.cp(base_angle, 5, eigen_qubit)
        circuit.cp(base_angle, 5, eigen_qubit)
        circuit.cp(base_angle, 5, eigen_qubit)
        circuit.cp(base_angle, 5, eigen_qubit)
        circuit.cp(base_angle, 5, eigen_qubit)
        circuit.cp(base_angle, 5, eigen_qubit)
        circuit.cp(base_angle, 5, eigen_qubit)
        circuit.cp(base_angle, 5, eigen_qubit)
        circuit.cp(base_angle, 5, eigen_qubit)
        circuit.cp(base_angle, 5, eigen_qubit)
        circuit.cp(base_angle, 5, eigen_qubit)
        circuit.cp(base_angle, 5, eigen_qubit)
        circuit.cp(base_angle, 5, eigen_qubit)
        circuit.cp(base_angle, 5, eigen_qubit)
        circuit.cp(base_angle, 5, eigen_qubit)
        circuit.cp(base_angle, 5, eigen_qubit)
        circuit.cp(base_angle, 5, eigen_qubit)
        circuit.cp(base_angle, 5, eigen_qubit)
        circuit.cp(base_angle, 5, eigen_qubit)
        circuit.cp(base_angle, 5, eigen_qubit)
        circuit.cp(base_angle, 5, eigen_qubit)
        circuit.cp(base_angle, 5, eigen_qubit)
        circuit.cp(base_angle, 5, eigen_qubit)
        circuit.cp(base_angle, 5, eigen_qubit)
        circuit.cp(base_angle, 5, eigen_qubit)
        circuit.cp(base_angle, 5, eigen_qubit)
        circuit.cp(base_angle, 5, eigen_qubit)

    circuit.barrier()

    circuit.swap(0, 5)
    circuit.swap(1, 4)
    circuit.swap(2, 3)

    circuit.h(0)

    circuit.cp(-np.pi / 2, 0, 1)
    circuit.h(1)

    circuit.cp(-np.pi / 4, 0, 2)
    circuit.cp(-np.pi / 2, 1, 2)
    circuit.h(2)

    circuit.cp(-np.pi / 8, 0, 3)
    circuit.cp(-np.pi / 4, 1, 3)
    circuit.cp(-np.pi / 2, 2, 3)
    circuit.h(3)

    circuit.cp(-np.pi / 16, 0, 4)
    circuit.cp(-np.pi / 8, 1, 4)
    circuit.cp(-np.pi / 4, 2, 4)
    circuit.cp(-np.pi / 2, 3, 4)
    circuit.h(4)

    circuit.cp(-np.pi / 32, 0, 5)
    circuit.cp(-np.pi / 16, 1, 5)
    circuit.cp(-np.pi / 8, 2, 5)
    circuit.cp(-np.pi / 4, 3, 5)
    circuit.cp(-np.pi / 2, 4, 5)
    circuit.h(5)

    circuit.barrier()

    circuit.measure(0, 0)
    circuit.measure(1, 1)
    circuit.measure(2, 2)
    circuit.measure(3, 3)
    circuit.measure(4, 4)
    circuit.measure(5, 5)
    return circuit


def build_program() -> QuantumCircuit:
    return build_circuit()


def run_program(config: ExecutionConfig) -> ExecutionResult:
    backend = get_backend(config.backend)
    transpiled = transpile(build_circuit(), backend)
    run_kwargs = {"shots": config.shots}
    if config.seed is not None:
        run_kwargs["seed_simulator"] = config.seed
    job = backend.run(transpiled, **run_kwargs)
    counts = normalize_counts(job.result().get_counts())
    metadata = dict(config.metadata)
    metadata.update(
        {
            "counting_qubits": COUNTING_QUBITS,
            "phase_numerator": PHASE_NUMERATOR,
            "phase_denominator": PHASE_DENOMINATOR,
            "expected_phase_bitstring": EXPECTED_PHASE_BITSTRING,
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
    task_id="QAB32",
    build_program=build_program,
    run_program=run_program,
    evaluate_gold_assertion=_placeholder_gold_assertion,
)
