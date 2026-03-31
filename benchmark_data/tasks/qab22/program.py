from __future__ import annotations

import math

from qiskit import QuantumCircuit, transpile

from qasserbench.execution.backends import get_backend
from qasserbench.execution.interfaces import (
    ExecutionConfig,
    ExecutionResult,
    GoldAssertionResult,
    ProgramDefinition,
)
from qasserbench.execution.runtime import normalize_counts


EXPECTED_STATE = "101"


def prepare_input(circuit: QuantumCircuit) -> None:
    circuit.x(0)
    circuit.x(2)


def apply_qft(circuit: QuantumCircuit, qubit_count: int = 3) -> None:
    for target in range(qubit_count):
        for control in range(target):
            angle = math.pi / (2 ** (target - control))
            circuit.cp(angle, control, target)
        circuit.h(target)


def apply_inverse_qft(circuit: QuantumCircuit, qubit_count: int = 3) -> None:
    for target in reversed(range(qubit_count)):
        circuit.h(target)
        for control in reversed(range(target)):
            angle = -math.pi / (2 ** (target - control))
            circuit.cp(angle, control, target)


def build_circuit() -> QuantumCircuit:
    circuit = QuantumCircuit(3, 3)
    prepare_input(circuit)
    apply_qft(circuit, 3)
    apply_inverse_qft(circuit, 3)
    circuit.measure(range(3), range(3))
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
    metadata["expected_state"] = EXPECTED_STATE
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
    task_id="QAB22",
    build_program=build_program,
    run_program=run_program,
    evaluate_gold_assertion=_placeholder_gold_assertion,
)
