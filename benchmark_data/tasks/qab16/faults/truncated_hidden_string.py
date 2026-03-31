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


DEFAULT_HIDDEN_STRING = "111"


def apply_oracle(circuit: QuantumCircuit, hidden_string: str) -> None:
    ancilla_index = len(hidden_string)
    for qubit, bit in enumerate(hidden_string[:-1]):
        if bit == "1":
            circuit.cx(qubit, ancilla_index)


def build_circuit(hidden_string: str = DEFAULT_HIDDEN_STRING) -> QuantumCircuit:
    input_qubit_count = len(hidden_string)
    ancilla_index = input_qubit_count
    circuit = QuantumCircuit(input_qubit_count + 1, input_qubit_count)
    circuit.x(ancilla_index)
    for qubit in range(input_qubit_count + 1):
        circuit.h(qubit)
    apply_oracle(circuit, hidden_string)
    for qubit in range(input_qubit_count):
        circuit.h(qubit)
        circuit.measure(qubit, qubit)
    return circuit


def build_program() -> QuantumCircuit:
    return build_circuit()


def run_program(config: ExecutionConfig) -> ExecutionResult:
    hidden_string = str(config.metadata.get("hidden_string", DEFAULT_HIDDEN_STRING))
    backend = get_backend(config.backend)
    transpiled = transpile(build_circuit(hidden_string), backend)
    run_kwargs = {"shots": config.shots}
    if config.seed is not None:
        run_kwargs["seed_simulator"] = config.seed
    job = backend.run(transpiled, **run_kwargs)
    counts = normalize_counts(job.result().get_counts())
    metadata = dict(config.metadata)
    metadata["hidden_string"] = hidden_string
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
    task_id="QAB16",
    build_program=build_program,
    run_program=run_program,
    evaluate_gold_assertion=_placeholder_gold_assertion,
)
