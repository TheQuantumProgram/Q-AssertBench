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


COUNTING_QUBITS = 8
WORK_QUBITS = 7
TOTAL_QUBITS = COUNTING_QUBITS + WORK_QUBITS


def entangle_order_finding_register(circuit: QuantumCircuit) -> None:
    for counting_qubit in range(COUNTING_QUBITS):
        for work_offset in range(WORK_QUBITS):
            circuit.cx(counting_qubit, COUNTING_QUBITS + work_offset)


def apply_inverse_qft(circuit: QuantumCircuit) -> None:
    for left in range(COUNTING_QUBITS // 2):
        circuit.swap(left, COUNTING_QUBITS - left - 1)

    for target in range(COUNTING_QUBITS):
        circuit.h(target)
        for control in range(target + 1, COUNTING_QUBITS):
            angle = -np.pi / (2 ** (control - target))
            circuit.cp(angle, control, target)


def build_circuit(*, include_phase_entanglement: bool = True) -> QuantumCircuit:
    circuit = QuantumCircuit(TOTAL_QUBITS, COUNTING_QUBITS)

    for qubit in range(COUNTING_QUBITS):
        circuit.h(qubit)

    if include_phase_entanglement:
        entangle_order_finding_register(circuit)

    apply_inverse_qft(circuit)
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
            "work_qubits": WORK_QUBITS,
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
    task_id="QAB30",
    build_program=build_program,
    run_program=run_program,
    evaluate_gold_assertion=_placeholder_gold_assertion,
)
