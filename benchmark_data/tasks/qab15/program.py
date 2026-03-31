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


HIDDEN_STRING = "111"
INPUT_QUBIT_COUNT = len(HIDDEN_STRING)


def apply_oracle(circuit: QuantumCircuit, hidden_string: str = HIDDEN_STRING) -> None:
    ancilla_index = len(hidden_string)
    for qubit, bit in enumerate(hidden_string):
        if bit == "1":
            circuit.cx(qubit, ancilla_index)


def build_circuit(hidden_string: str = HIDDEN_STRING) -> QuantumCircuit:
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


def build_state_preparation_probe_circuit() -> QuantumCircuit:
    circuit = QuantumCircuit(INPUT_QUBIT_COUNT, INPUT_QUBIT_COUNT)
    for qubit in range(INPUT_QUBIT_COUNT):
        circuit.h(qubit)
        circuit.measure(qubit, qubit)
    return circuit


def build_program() -> QuantumCircuit:
    return build_circuit()


def run_program(config: ExecutionConfig) -> ExecutionResult:
    backend = get_backend(config.backend)
    transpiled = transpile(build_state_preparation_probe_circuit(), backend)
    run_kwargs = {"shots": config.shots}
    if config.seed is not None:
        run_kwargs["seed_simulator"] = config.seed
    job = backend.run(transpiled, **run_kwargs)
    counts = normalize_counts(job.result().get_counts())
    metadata = dict(config.metadata)
    metadata["observation_stage"] = "after_state_preparation"
    metadata["num_input_qubits"] = INPUT_QUBIT_COUNT
    metadata["hidden_string"] = HIDDEN_STRING
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
    task_id="QAB15",
    build_program=build_program,
    run_program=run_program,
    evaluate_gold_assertion=_placeholder_gold_assertion,
)
