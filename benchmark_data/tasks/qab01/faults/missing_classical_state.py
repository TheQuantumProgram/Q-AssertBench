from __future__ import annotations

from math import pi

from qiskit import QuantumCircuit
from qasserbench.execution.backends import get_backend

from qasserbench.execution.interfaces import (
    ExecutionConfig,
    ExecutionResult,
    GoldAssertionResult,
    ProgramDefinition,
)
from qasserbench.execution.runtime import normalize_counts


def build_circuit() -> QuantumCircuit:
    qc = QuantumCircuit(5, 5)
    qc.h(0)
    qc.h(1)
    qc.h(2)
    qc.u(2 * pi / 3, 0, 0, 3)
    qc.u(2 * pi / 9, 0, 0, 4)
    qc.measure(range(5), range(5))
    return qc


def build_program() -> QuantumCircuit:
    return build_circuit()


def run_program(config: ExecutionConfig) -> ExecutionResult:
    backend = get_backend(config.backend)
    run_kwargs = {"shots": config.shots}
    if config.seed is not None:
        run_kwargs["seed_simulator"] = config.seed
    job = backend.run(build_circuit(), **run_kwargs)
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
    task_id="QAB01",
    build_program=build_program,
    run_program=run_program,
    evaluate_gold_assertion=_placeholder_gold_assertion,
)
