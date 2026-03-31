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

    for qubit in range(QUBIT_COUNT):
        circuit.h(qubit)

    for layer_index, (gamma, beta) in enumerate(zip(LAYER_GAMMAS, LAYER_BETAS)):
        for edge_index, (control, target) in enumerate(CYCLE_EDGES):
            if layer_index == 4 and edge_index == 3:
                continue
            circuit.h(target)
            circuit.cz(control, target)
            circuit.h(target)
            circuit.rz(2 * gamma, target)
            circuit.h(target)
            circuit.cz(control, target)
            circuit.h(target)
        for qubit in range(QUBIT_COUNT):
            circuit.rx(2 * beta, qubit)

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
            "good_states": sorted(GOOD_STATES),
            "cycle_edges": [list(edge) for edge in CYCLE_EDGES],
            "layer_gammas": list(LAYER_GAMMAS),
            "layer_betas": list(LAYER_BETAS),
            "fault": "missing_cost_edge",
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
