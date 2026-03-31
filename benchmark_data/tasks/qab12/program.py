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


DEFAULT_ORACLE_TYPE = 0


def apply_oracle(circuit: QuantumCircuit, oracle_type: int) -> None:
    if oracle_type == 0:
        return
    if oracle_type == 1:
        circuit.cx(0, 1)
        return
    raise ValueError("oracle_type must be 0 or 1")


def build_circuit(oracle_type: int = DEFAULT_ORACLE_TYPE) -> QuantumCircuit:
    circuit = QuantumCircuit(2, 1)
    circuit.x(1)
    circuit.h(0)
    circuit.h(1)
    apply_oracle(circuit, oracle_type)
    circuit.h(0)
    circuit.measure(0, 0)
    return circuit


def build_program() -> QuantumCircuit:
    return build_circuit()


def run_program(config: ExecutionConfig) -> ExecutionResult:
    oracle_type = int(config.metadata.get("oracle_type", DEFAULT_ORACLE_TYPE))
    backend = get_backend(config.backend)
    transpiled = transpile(build_circuit(oracle_type), backend)
    run_kwargs = {"shots": config.shots}
    if config.seed is not None:
        run_kwargs["seed_simulator"] = config.seed
    job = backend.run(transpiled, **run_kwargs)
    counts = normalize_counts(job.result().get_counts())
    metadata = dict(config.metadata)
    metadata["oracle_type"] = oracle_type
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
    task_id="QAB12",
    build_program=build_program,
    run_program=run_program,
    evaluate_gold_assertion=_placeholder_gold_assertion,
)
