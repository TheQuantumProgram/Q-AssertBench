from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector

from qasserbench.execution.backends import get_backend
from qasserbench.execution.interfaces import (
    ExecutionConfig,
    ExecutionResult,
    GoldAssertionResult,
    ProgramDefinition,
)
from qasserbench.execution.runtime import normalize_counts


NUM_QUBITS = 10
PERIOD = 4
EXPECTED_PEAK_CENTERS = tuple(k * (2**NUM_QUBITS // PERIOD) for k in range(PERIOD))


def prepare_periodic_input(circuit: QuantumCircuit, *, period: int = PERIOD) -> None:
    state_indexes = list(range(0, 2**NUM_QUBITS, period))
    amplitudes = np.zeros(2**NUM_QUBITS, dtype=complex)
    amplitude = 1 / np.sqrt(len(state_indexes))
    for index in state_indexes:
        amplitudes[index] = amplitude
    circuit.initialize(Statevector(amplitudes).data, range(NUM_QUBITS))


def apply_qft(circuit: QuantumCircuit, *, include_output_reversal: bool = True) -> None:
    for target in range(NUM_QUBITS):
        circuit.h(target)
        for control in range(target + 1, NUM_QUBITS):
            angle = np.pi / (2 ** (control - target))
            circuit.cp(angle, control, target)

    if include_output_reversal:
        for left in range(NUM_QUBITS // 2):
            circuit.swap(left, NUM_QUBITS - left - 1)


def build_circuit(*, include_output_reversal: bool = True) -> QuantumCircuit:
    circuit = QuantumCircuit(NUM_QUBITS, NUM_QUBITS)
    prepare_periodic_input(circuit)
    apply_qft(circuit, include_output_reversal=include_output_reversal)
    circuit.measure(range(NUM_QUBITS), range(NUM_QUBITS))
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
            "period": PERIOD,
            "expected_peak_centers": list(EXPECTED_PEAK_CENTERS),
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
    task_id="QAB29",
    build_program=build_program,
    run_program=run_program,
    evaluate_gold_assertion=_placeholder_gold_assertion,
)
