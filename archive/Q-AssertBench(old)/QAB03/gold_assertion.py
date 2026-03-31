import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import Aer
from qiskit.circuit.library import U3Gate


class SwapCircuitWithAssertion:
    def __init__(self):
        self.qc = QuantumCircuit(3, 3)
        self.expected_prob_q0 = None
        self._initialize_qubits()
        self._apply_swaps()
        self.qc.measure([0, 1, 2], [0, 1, 2])
        self.counts = None

    def _initialize_qubits(self):
        # Probabilities for q0, q1, q2
        probs = [0.2, 0.5, 0.7]

        for i, p in enumerate(probs):
            theta = 2 * np.arcsin(np.sqrt(p))
            self.qc.append(U3Gate(theta, 0, 0), [i])

        # After swaps, q0 will hold initial state of q?

    def _apply_swaps(self):
        self.qc.swap(2, 1)
        self.qc.swap(0, 1)

    def run_and_assert(self, shots=1024, tolerance=0.1):
        backend = Aer.get_backend("qasm_simulator")
        job = backend.run(self.qc, shots=shots)
        result = job.result()
        self.counts = result.get_counts()

        # Measure probability of q0 = 1
        counts_1 = sum(v for k, v in self.counts.items() if k[-1] == "1")
        prob_q0 = counts_1 / shots

        assert abs(prob_q0 - 0.7) < tolerance, (
            f"q0 measured probability {prob_q0:.3f} "
            f"does not match expected {self.expected_prob_q0:.3f}"
        )


if __name__ == "__main__":
    circuit = SwapCircuitWithAssertion()
    circuit.run_and_assert()
