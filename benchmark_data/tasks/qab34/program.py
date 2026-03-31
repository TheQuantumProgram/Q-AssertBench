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


QUBIT_COUNT = 6
CYCLE_EDGES = ((0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0))
GOOD_STATES = {"010101", "101010"}
LAYER_GAMMAS = (0.046, 0.904, 0.686, 0.229, 0.789, 0.35)
LAYER_BETAS = (0.054, 0.631, 0.013, 0.659, 0.123, 0.576)


def build_circuit() -> QuantumCircuit:
    circuit = QuantumCircuit(QUBIT_COUNT, QUBIT_COUNT)

    circuit.h(0)
    circuit.h(1)
    circuit.h(2)
    circuit.h(3)
    circuit.h(4)
    circuit.h(5)

    circuit.barrier()  # layer 1 cost
    circuit.h(1)
    circuit.cz(0, 1)
    circuit.h(1)
    circuit.rz(0.092, 1)
    circuit.h(1)
    circuit.cz(0, 1)
    circuit.h(1)
    circuit.h(2)
    circuit.cz(1, 2)
    circuit.h(2)
    circuit.rz(0.092, 2)
    circuit.h(2)
    circuit.cz(1, 2)
    circuit.h(2)
    circuit.h(3)
    circuit.cz(2, 3)
    circuit.h(3)
    circuit.rz(0.092, 3)
    circuit.h(3)
    circuit.cz(2, 3)
    circuit.h(3)
    circuit.h(4)
    circuit.cz(3, 4)
    circuit.h(4)
    circuit.rz(0.092, 4)
    circuit.h(4)
    circuit.cz(3, 4)
    circuit.h(4)
    circuit.h(5)
    circuit.cz(4, 5)
    circuit.h(5)
    circuit.rz(0.092, 5)
    circuit.h(5)
    circuit.cz(4, 5)
    circuit.h(5)
    circuit.h(0)
    circuit.cz(5, 0)
    circuit.h(0)
    circuit.rz(0.092, 0)
    circuit.h(0)
    circuit.cz(5, 0)
    circuit.h(0)

    circuit.barrier()  # layer 1 mixer
    circuit.rx(0.108, 0)
    circuit.rx(0.108, 1)
    circuit.rx(0.108, 2)
    circuit.rx(0.108, 3)
    circuit.rx(0.108, 4)
    circuit.rx(0.108, 5)

    circuit.barrier()  # layer 2 cost
    circuit.h(1)
    circuit.cz(0, 1)
    circuit.h(1)
    circuit.rz(1.808, 1)
    circuit.h(1)
    circuit.cz(0, 1)
    circuit.h(1)
    circuit.h(2)
    circuit.cz(1, 2)
    circuit.h(2)
    circuit.rz(1.808, 2)
    circuit.h(2)
    circuit.cz(1, 2)
    circuit.h(2)
    circuit.h(3)
    circuit.cz(2, 3)
    circuit.h(3)
    circuit.rz(1.808, 3)
    circuit.h(3)
    circuit.cz(2, 3)
    circuit.h(3)
    circuit.h(4)
    circuit.cz(3, 4)
    circuit.h(4)
    circuit.rz(1.808, 4)
    circuit.h(4)
    circuit.cz(3, 4)
    circuit.h(4)
    circuit.h(5)
    circuit.cz(4, 5)
    circuit.h(5)
    circuit.rz(1.808, 5)
    circuit.h(5)
    circuit.cz(4, 5)
    circuit.h(5)
    circuit.h(0)
    circuit.cz(5, 0)
    circuit.h(0)
    circuit.rz(1.808, 0)
    circuit.h(0)
    circuit.cz(5, 0)
    circuit.h(0)

    circuit.barrier()  # layer 2 mixer
    circuit.rx(1.262, 0)
    circuit.rx(1.262, 1)
    circuit.rx(1.262, 2)
    circuit.rx(1.262, 3)
    circuit.rx(1.262, 4)
    circuit.rx(1.262, 5)

    circuit.barrier()  # layer 3 cost
    circuit.h(1)
    circuit.cz(0, 1)
    circuit.h(1)
    circuit.rz(1.372, 1)
    circuit.h(1)
    circuit.cz(0, 1)
    circuit.h(1)
    circuit.h(2)
    circuit.cz(1, 2)
    circuit.h(2)
    circuit.rz(1.372, 2)
    circuit.h(2)
    circuit.cz(1, 2)
    circuit.h(2)
    circuit.h(3)
    circuit.cz(2, 3)
    circuit.h(3)
    circuit.rz(1.372, 3)
    circuit.h(3)
    circuit.cz(2, 3)
    circuit.h(3)
    circuit.h(4)
    circuit.cz(3, 4)
    circuit.h(4)
    circuit.rz(1.372, 4)
    circuit.h(4)
    circuit.cz(3, 4)
    circuit.h(4)
    circuit.h(5)
    circuit.cz(4, 5)
    circuit.h(5)
    circuit.rz(1.372, 5)
    circuit.h(5)
    circuit.cz(4, 5)
    circuit.h(5)
    circuit.h(0)
    circuit.cz(5, 0)
    circuit.h(0)
    circuit.rz(1.372, 0)
    circuit.h(0)
    circuit.cz(5, 0)
    circuit.h(0)

    circuit.barrier()  # layer 3 mixer
    circuit.rx(0.026, 0)
    circuit.rx(0.026, 1)
    circuit.rx(0.026, 2)
    circuit.rx(0.026, 3)
    circuit.rx(0.026, 4)
    circuit.rx(0.026, 5)

    circuit.barrier()  # layer 4 cost
    circuit.h(1)
    circuit.cz(0, 1)
    circuit.h(1)
    circuit.rz(0.458, 1)
    circuit.h(1)
    circuit.cz(0, 1)
    circuit.h(1)
    circuit.h(2)
    circuit.cz(1, 2)
    circuit.h(2)
    circuit.rz(0.458, 2)
    circuit.h(2)
    circuit.cz(1, 2)
    circuit.h(2)
    circuit.h(3)
    circuit.cz(2, 3)
    circuit.h(3)
    circuit.rz(0.458, 3)
    circuit.h(3)
    circuit.cz(2, 3)
    circuit.h(3)
    circuit.h(4)
    circuit.cz(3, 4)
    circuit.h(4)
    circuit.rz(0.458, 4)
    circuit.h(4)
    circuit.cz(3, 4)
    circuit.h(4)
    circuit.h(5)
    circuit.cz(4, 5)
    circuit.h(5)
    circuit.rz(0.458, 5)
    circuit.h(5)
    circuit.cz(4, 5)
    circuit.h(5)
    circuit.h(0)
    circuit.cz(5, 0)
    circuit.h(0)
    circuit.rz(0.458, 0)
    circuit.h(0)
    circuit.cz(5, 0)
    circuit.h(0)

    circuit.barrier()  # layer 4 mixer
    circuit.rx(1.318, 0)
    circuit.rx(1.318, 1)
    circuit.rx(1.318, 2)
    circuit.rx(1.318, 3)
    circuit.rx(1.318, 4)
    circuit.rx(1.318, 5)

    circuit.barrier()  # layer 5 cost
    circuit.h(1)
    circuit.cz(0, 1)
    circuit.h(1)
    circuit.rz(1.578, 1)
    circuit.h(1)
    circuit.cz(0, 1)
    circuit.h(1)
    circuit.h(2)
    circuit.cz(1, 2)
    circuit.h(2)
    circuit.rz(1.578, 2)
    circuit.h(2)
    circuit.cz(1, 2)
    circuit.h(2)
    circuit.h(3)
    circuit.cz(2, 3)
    circuit.h(3)
    circuit.rz(1.578, 3)
    circuit.h(3)
    circuit.cz(2, 3)
    circuit.h(3)
    circuit.h(4)
    circuit.cz(3, 4)
    circuit.h(4)
    circuit.rz(1.578, 4)
    circuit.h(4)
    circuit.cz(3, 4)
    circuit.h(4)
    circuit.h(5)
    circuit.cz(4, 5)
    circuit.h(5)
    circuit.rz(1.578, 5)
    circuit.h(5)
    circuit.cz(4, 5)
    circuit.h(5)
    circuit.h(0)
    circuit.cz(5, 0)
    circuit.h(0)
    circuit.rz(1.578, 0)
    circuit.h(0)
    circuit.cz(5, 0)
    circuit.h(0)

    circuit.barrier()  # layer 5 mixer
    circuit.rx(0.246, 0)
    circuit.rx(0.246, 1)
    circuit.rx(0.246, 2)
    circuit.rx(0.246, 3)
    circuit.rx(0.246, 4)
    circuit.rx(0.246, 5)

    circuit.barrier()  # layer 6 cost
    circuit.h(1)
    circuit.cz(0, 1)
    circuit.h(1)
    circuit.rz(0.7, 1)
    circuit.h(1)
    circuit.cz(0, 1)
    circuit.h(1)
    circuit.h(2)
    circuit.cz(1, 2)
    circuit.h(2)
    circuit.rz(0.7, 2)
    circuit.h(2)
    circuit.cz(1, 2)
    circuit.h(2)
    circuit.h(3)
    circuit.cz(2, 3)
    circuit.h(3)
    circuit.rz(0.7, 3)
    circuit.h(3)
    circuit.cz(2, 3)
    circuit.h(3)
    circuit.h(4)
    circuit.cz(3, 4)
    circuit.h(4)
    circuit.rz(0.7, 4)
    circuit.h(4)
    circuit.cz(3, 4)
    circuit.h(4)
    circuit.h(5)
    circuit.cz(4, 5)
    circuit.h(5)
    circuit.rz(0.7, 5)
    circuit.h(5)
    circuit.cz(4, 5)
    circuit.h(5)
    circuit.h(0)
    circuit.cz(5, 0)
    circuit.h(0)
    circuit.rz(0.7, 0)
    circuit.h(0)
    circuit.cz(5, 0)
    circuit.h(0)

    circuit.barrier()  # layer 6 mixer
    circuit.rx(1.152, 0)
    circuit.rx(1.152, 1)
    circuit.rx(1.152, 2)
    circuit.rx(1.152, 3)
    circuit.rx(1.152, 4)
    circuit.rx(1.152, 5)

    circuit.barrier()
    circuit.measure(0, 0)
    circuit.measure(1, 1)
    circuit.measure(2, 2)
    circuit.measure(3, 3)
    circuit.measure(4, 4)
    circuit.measure(5, 5)
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
            "good_states": sorted(GOOD_STATES),
            "cycle_edges": [list(edge) for edge in CYCLE_EDGES],
            "layer_gammas": list(LAYER_GAMMAS),
            "layer_betas": list(LAYER_BETAS),
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
    task_id="QAB34",
    build_program=build_program,
    run_program=run_program,
    evaluate_gold_assertion=_placeholder_gold_assertion,
)
