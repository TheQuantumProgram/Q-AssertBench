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

    circuit.barrier()

    circuit.cx(1, 7)
    circuit.cx(1, 0)
    circuit.h(1)
    circuit.cx(7, 1)
    circuit.tdg(1)
    circuit.cx(0, 1)
    circuit.t(1)
    circuit.cx(7, 1)
    circuit.tdg(1)
    circuit.cx(0, 1)
    circuit.t(7)
    circuit.t(1)
    circuit.h(1)
    circuit.cx(0, 7)
    circuit.t(0)
    circuit.tdg(7)
    circuit.cx(0, 7)

    circuit.cx(2, 8)
    circuit.cx(2, 1)
    circuit.h(2)
    circuit.cx(8, 2)
    circuit.tdg(2)
    circuit.cx(1, 2)
    circuit.t(2)
    circuit.cx(8, 2)
    circuit.tdg(2)
    circuit.cx(1, 2)
    circuit.t(8)
    circuit.t(2)
    circuit.h(2)
    circuit.cx(1, 8)
    circuit.t(1)
    circuit.tdg(8)
    circuit.cx(1, 8)

    circuit.cx(3, 9)
    circuit.cx(3, 2)
    circuit.h(3)
    circuit.cx(9, 3)
    circuit.tdg(3)
    circuit.cx(2, 3)
    circuit.t(3)
    circuit.cx(9, 3)
    circuit.tdg(3)
    circuit.cx(2, 3)
    circuit.t(9)
    circuit.t(3)
    circuit.h(3)
    circuit.cx(2, 9)
    circuit.t(2)
    circuit.tdg(9)
    circuit.cx(2, 9)

    circuit.cx(4, 10)
    circuit.cx(4, 3)
    circuit.h(4)
    circuit.cx(10, 4)
    circuit.tdg(4)
    circuit.cx(3, 4)
    circuit.t(4)
    circuit.cx(10, 4)
    circuit.tdg(4)
    circuit.cx(3, 4)
    circuit.t(10)
    circuit.t(4)
    circuit.h(4)
    circuit.cx(3, 10)
    circuit.t(3)
    circuit.tdg(10)
    circuit.cx(3, 10)

    circuit.cx(5, 11)
    circuit.cx(5, 4)
    circuit.h(5)
    circuit.cx(11, 5)
    circuit.tdg(5)
    circuit.cx(4, 5)
    circuit.t(5)
    circuit.cx(11, 5)
    circuit.tdg(5)
    circuit.cx(4, 5)
    circuit.t(11)
    circuit.t(5)
    circuit.h(5)
    circuit.cx(4, 11)
    circuit.t(4)
    circuit.tdg(11)
    circuit.cx(4, 11)

    circuit.cx(6, 12)
    circuit.cx(6, 5)
    circuit.h(6)
    circuit.cx(12, 6)
    circuit.tdg(6)
    circuit.cx(5, 6)
    circuit.t(6)
    circuit.cx(12, 6)
    circuit.tdg(6)
    circuit.cx(5, 6)
    circuit.t(12)
    circuit.t(6)
    circuit.h(6)
    circuit.cx(5, 12)
    circuit.t(5)
    circuit.tdg(12)
    circuit.cx(5, 12)

    circuit.cx(6, 13)

    circuit.h(6)
    circuit.cx(12, 6)
    circuit.tdg(6)
    circuit.cx(5, 6)
    circuit.t(6)
    circuit.cx(12, 6)
    circuit.tdg(6)
    circuit.cx(5, 6)
    circuit.t(12)
    circuit.t(6)
    circuit.h(6)
    circuit.cx(5, 12)
    circuit.t(5)
    circuit.tdg(12)
    circuit.cx(5, 12)
    circuit.cx(6, 5)
    circuit.cx(5, 12)

    circuit.h(5)
    circuit.cx(11, 5)
    circuit.tdg(5)
    circuit.cx(4, 5)
    circuit.t(5)
    circuit.cx(11, 5)
    circuit.tdg(5)
    circuit.cx(4, 5)
    circuit.t(11)
    circuit.t(5)
    circuit.h(5)
    circuit.cx(4, 11)
    circuit.t(4)
    circuit.tdg(11)
    circuit.cx(4, 11)
    circuit.cx(5, 4)
    circuit.cx(4, 11)

    circuit.h(4)
    circuit.cx(10, 4)
    circuit.tdg(4)
    circuit.cx(3, 4)
    circuit.t(4)
    circuit.cx(10, 4)
    circuit.tdg(4)
    circuit.cx(3, 4)
    circuit.t(10)
    circuit.t(4)
    circuit.h(4)
    circuit.cx(3, 10)
    circuit.t(3)
    circuit.tdg(10)
    circuit.cx(3, 10)
    circuit.cx(4, 3)
    circuit.cx(3, 10)

    circuit.h(3)
    circuit.cx(9, 3)
    circuit.tdg(3)
    circuit.cx(2, 3)
    circuit.t(3)
    circuit.cx(9, 3)
    circuit.tdg(3)
    circuit.cx(2, 3)
    circuit.t(9)
    circuit.t(3)
    circuit.h(3)
    circuit.cx(2, 9)
    circuit.t(2)
    circuit.tdg(9)
    circuit.cx(2, 9)
    circuit.cx(3, 2)
    circuit.cx(2, 9)

    circuit.h(2)
    circuit.cx(8, 2)
    circuit.tdg(2)
    circuit.cx(1, 2)
    circuit.t(2)
    circuit.cx(8, 2)
    circuit.tdg(2)
    circuit.cx(1, 2)
    circuit.t(8)
    circuit.t(2)
    circuit.h(2)
    circuit.cx(1, 8)
    circuit.t(1)
    circuit.tdg(8)
    circuit.cx(1, 8)
    circuit.cx(2, 1)
    circuit.cx(1, 8)

    circuit.h(1)
    circuit.cx(7, 1)
    circuit.tdg(1)
    circuit.cx(0, 1)
    circuit.t(1)
    circuit.cx(7, 1)
    circuit.tdg(1)
    circuit.cx(0, 1)
    circuit.t(7)
    circuit.t(1)
    circuit.h(1)
    circuit.cx(0, 7)
    circuit.t(0)
    circuit.tdg(7)
    circuit.cx(0, 7)
    circuit.cx(1, 0)
    circuit.cx(0, 7)

    circuit.barrier()

    circuit.measure(0, 0)
    circuit.measure(1, 1)
    circuit.measure(2, 2)
    circuit.measure(3, 3)
    circuit.measure(4, 4)
    circuit.measure(5, 5)
    circuit.measure(6, 6)
    circuit.measure(7, 7)
    circuit.measure(8, 8)
    circuit.measure(9, 9)
    circuit.measure(10, 10)
    circuit.measure(11, 11)
    circuit.measure(12, 12)
    circuit.measure(13, 13)
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
