from __future__ import annotations

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


QUBIT_COUNT = 5
COLLAPSED_STATE = "10000"


def build_statevector() -> Statevector:
    amplitudes = [0.0j] * (2**QUBIT_COUNT)
    amplitudes[int(COLLAPSED_STATE, 2)] = 1.0
    return Statevector(amplitudes)


def build_circuit() -> QuantumCircuit:
    circuit = QuantumCircuit(QUBIT_COUNT, QUBIT_COUNT)
    circuit.initialize(build_statevector().data, range(QUBIT_COUNT))
    circuit.measure(range(QUBIT_COUNT), range(QUBIT_COUNT))
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
            "support_family": "single_excitation_collapsed",
            "collapsed_state": COLLAPSED_STATE,
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
    task_id="QAB37",
    build_program=build_program,
    run_program=run_program,
    evaluate_gold_assertion=_placeholder_gold_assertion,
)
