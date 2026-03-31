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


def build_circuit() -> QuantumCircuit:
    circuit = QuantumCircuit(TOTAL_QUBITS, COUNTING_QUBITS)
    eigen_qubit = COUNTING_QUBITS
    base_angle = 2 * np.pi * PHASE_NUMERATOR / PHASE_DENOMINATOR

    circuit.x(eigen_qubit)
    for qubit in range(COUNTING_QUBITS):
        circuit.h(qubit)

    for control in range(COUNTING_QUBITS - 1):
        for _ in range(2**control):
            circuit.cp(base_angle, control, eigen_qubit)

    for left in range(COUNTING_QUBITS // 2):
        circuit.swap(left, COUNTING_QUBITS - left - 1)

    for target_index in range(COUNTING_QUBITS):
        for control_index in range(target_index):
            angle = -np.pi / (2 ** (target_index - control_index))
            circuit.cp(angle, control_index, target_index)
        circuit.h(target_index)

    circuit.measure(range(COUNTING_QUBITS), range(COUNTING_QUBITS))
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
            "fault": "missing_phase_layer",
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
