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


QUBIT_COUNT = 14
INPUT_A = "100101"
INPUT_B = "011010"
EXPECTED_SUM_BITS = "0111111"
EXPECTED_OUTPUT_BITSTRING = "01111111001010"


def build_circuit() -> QuantumCircuit:
    circuit = QuantumCircuit(QUBIT_COUNT, QUBIT_COUNT)

    circuit.x(1)
    circuit.x(3)
    circuit.x(6)
    circuit.x(8)
    circuit.x(10)
    circuit.x(11)

    circuit.cx(1, 7)
    circuit.cx(1, 0)
    circuit.ccx(0, 7, 1)
    circuit.cx(2, 8)
    circuit.cx(2, 1)
    circuit.ccx(1, 8, 2)
    circuit.cx(3, 9)
    circuit.cx(3, 2)
    circuit.ccx(2, 9, 3)
    circuit.cx(4, 10)
    circuit.cx(4, 3)
    circuit.ccx(3, 10, 4)
    circuit.cx(5, 11)
    circuit.cx(5, 4)
    circuit.ccx(4, 11, 5)
    circuit.cx(6, 12)
    circuit.cx(6, 5)
    circuit.cx(6, 13)
    circuit.ccx(5, 12, 6)
    circuit.cx(6, 5)
    circuit.cx(5, 12)
    circuit.ccx(4, 11, 5)
    circuit.cx(5, 4)
    circuit.cx(4, 11)
    circuit.ccx(3, 10, 4)
    circuit.cx(4, 3)
    circuit.cx(3, 10)
    circuit.ccx(2, 9, 3)
    circuit.cx(3, 2)
    circuit.cx(2, 9)
    circuit.ccx(1, 8, 2)
    circuit.cx(2, 1)
    circuit.cx(1, 8)
    circuit.ccx(0, 7, 1)
    circuit.cx(1, 0)
    circuit.cx(0, 7)
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
            "input_a": INPUT_A,
            "input_b": INPUT_B,
            "expected_sum_bits": EXPECTED_SUM_BITS,
            "expected_output_bitstring": EXPECTED_OUTPUT_BITSTRING,
            "fault": "missing_carry_propagation",
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
    task_id="QAB33",
    build_program=build_program,
    run_program=run_program,
    evaluate_gold_assertion=_placeholder_gold_assertion,
)
