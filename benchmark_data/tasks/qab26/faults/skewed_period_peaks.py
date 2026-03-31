from __future__ import annotations

from qiskit import QuantumCircuit, transpile

from qasserbench.execution.backends import get_backend
from qasserbench.execution.interfaces import (
    ExecutionConfig,
    ExecutionResult,
    GoldAssertionResult,
    ProgramDefinition,
)
from qasserbench.execution.runtime import normalize_counts


EXPECTED_PEAKS = {"00000", "00010", "00100", "00110"}


def build_circuit() -> QuantumCircuit:
    circuit = QuantumCircuit(5, 5)
    circuit.x(0)

    circuit.h(4)
    circuit.h(4)
    circuit.measure(4, 0)
    circuit.reset(4)

    circuit.h(4)
    circuit.cx(4, 2)
    circuit.cx(4, 0)
    circuit.h(4)
    circuit.measure(4, 1)
    circuit.reset(4)

    circuit.h(4)
    circuit.cswap(4, 3, 2)
    circuit.h(4)
    circuit.measure(4, 2)
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
    metadata["expected_peaks"] = sorted(EXPECTED_PEAKS)
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
    task_id="QAB26",
    build_program=build_program,
    run_program=run_program,
    evaluate_gold_assertion=_placeholder_gold_assertion,
)
