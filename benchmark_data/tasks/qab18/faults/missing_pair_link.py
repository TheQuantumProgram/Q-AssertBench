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


HIDDEN_PERIOD = "11"
INPUT_QUBIT_COUNT = len(HIDDEN_PERIOD)


def apply_oracle(circuit: QuantumCircuit) -> None:
    circuit.cx(0, 2)
    circuit.cx(1, 2)
    circuit.cx(1, 3)


def build_circuit() -> QuantumCircuit:
    circuit = QuantumCircuit(2 * INPUT_QUBIT_COUNT, INPUT_QUBIT_COUNT)
    for qubit in range(INPUT_QUBIT_COUNT):
        circuit.h(qubit)
    apply_oracle(circuit)
    for qubit in range(INPUT_QUBIT_COUNT):
        circuit.h(qubit)
        circuit.measure(qubit, qubit)
    return circuit


def build_pair_probe_circuit() -> QuantumCircuit:
    circuit = QuantumCircuit(2 * INPUT_QUBIT_COUNT, 2 * INPUT_QUBIT_COUNT)
    for qubit in range(INPUT_QUBIT_COUNT):
        circuit.h(qubit)
    apply_oracle(circuit)
    circuit.measure(2, 2)
    circuit.measure(3, 3)
    circuit.measure(0, 0)
    circuit.measure(1, 1)
    return circuit


def build_program() -> QuantumCircuit:
    return build_circuit()


def run_program(config: ExecutionConfig) -> ExecutionResult:
    backend = get_backend(config.backend)
    transpiled = transpile(build_pair_probe_circuit(), backend)
    run_kwargs = {"shots": config.shots}
    if config.seed is not None:
        run_kwargs["seed_simulator"] = config.seed
    job = backend.run(transpiled, **run_kwargs)
    counts = normalize_counts(job.result().get_counts())
    metadata = dict(config.metadata)
    metadata["observation_stage"] = "after_output_measurement"
    metadata["hidden_period"] = HIDDEN_PERIOD
    metadata["num_input_qubits"] = INPUT_QUBIT_COUNT
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
    task_id="QAB18",
    build_program=build_program,
    run_program=run_program,
    evaluate_gold_assertion=_placeholder_gold_assertion,
)
