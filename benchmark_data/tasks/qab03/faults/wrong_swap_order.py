from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import U3Gate
from qasserbench.execution.backends import get_backend

from qasserbench.execution.interfaces import (
    ExecutionConfig,
    ExecutionResult,
    GoldAssertionResult,
    ProgramDefinition,
)
from qasserbench.execution.runtime import normalize_counts


DEFAULT_PROBABILITIES = (0.2, 0.5, 0.7)


def build_circuit(
    probabilities: tuple[float, float, float] = DEFAULT_PROBABILITIES,
) -> QuantumCircuit:
    qc = QuantumCircuit(3, 3)

    for index, probability in enumerate(probabilities):
        theta = 2 * np.arcsin(np.sqrt(probability))
        qc.append(U3Gate(theta, 0, 0), [index])

    qc.swap(0, 1)
    qc.swap(2, 1)
    qc.measure([0, 1, 2], [0, 1, 2])
    return qc


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
    return ExecutionResult(
        counts=counts,
        shots=config.shots,
        backend=config.backend,
        metadata=dict(config.metadata),
    )


def _placeholder_gold_assertion(_: ExecutionResult) -> GoldAssertionResult:
    return GoldAssertionResult(
        passed=False,
        details={"note": "Loader should replace this placeholder gold evaluator."},
    )


PROGRAM = ProgramDefinition(
    task_id="QAB03",
    build_program=build_program,
    run_program=run_program,
    evaluate_gold_assertion=_placeholder_gold_assertion,
)
