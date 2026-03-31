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


DOMINANT_STATE = "000"
MIN_DOMINANT_RATIO = 0.6


def build_circuit() -> QuantumCircuit:
    circuit = QuantumCircuit(3, 3)

    circuit.h(1)
    circuit.cx(1, 0)
    circuit.rz(2 * np.pi / 3, 0)
    circuit.cx(1, 0)
    circuit.h(1)

    theta = 2 * np.arcsin(1 / 1.5)
    circuit.cry(theta, 1, 2)

    circuit.h(1)
    circuit.cx(1, 0)
    circuit.rz(-2 * np.pi / 3, 0)
    circuit.cx(1, 0)
    circuit.h(1)

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
    metadata["dominant_state"] = DOMINANT_STATE
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
    task_id="QAB28",
    build_program=build_program,
    run_program=run_program,
    evaluate_gold_assertion=_placeholder_gold_assertion,
)
