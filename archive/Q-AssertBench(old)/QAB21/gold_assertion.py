import math
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer


class QuantumFourierTransform:
    def __init__(self, n=3, shots=1024):
        self.n = n
        self.shots = shots
        self.backend = Aer.get_backend("qasm_simulator")

    def apply_qft(self, circuit):
        """Apply QFT on the first n qubits."""
        for j in range(self.n):
            circuit.h(j)
            for k in range(j + 1, self.n):
                angle = math.pi / float(2 ** (k - j))
                circuit.cp(angle, k, j)
        circuit.barrier()

    def build_and_run(self, prepare_input=None):
        circuit = QuantumCircuit(self.n, self.n)

        # Prepare input state
        if prepare_input:
            prepare_input(circuit)

        # Apply QFT
        self.apply_qft(circuit)

        # Measure
        circuit.measure(range(self.n), range(self.n))

        transpiled = transpile(circuit, self.backend)
        job = self.backend.run(transpiled, shots=self.shots)
        result = job.result()
        return result.get_counts()


if __name__ == "__main__":
    qft_runner = QuantumFourierTransform(n=3, shots=1024)

    # Prepare a periodic input: (|000⟩ + |100⟩)/√2
    def prepare_periodic(circuit):
        circuit.h(0)
        circuit.x(2)

    counts = qft_runner.build_and_run(prepare_input=prepare_periodic)

    # ----- GOLD ASSERTION START -----
    # Expect distribution not uniform: a few states dominate (>20% each)
    threshold = 0.20
    dominant_states = [state for state, cnt in counts.items() if cnt / qft_runner.shots > threshold]

    assert len(dominant_states) > 0, f"Expected peaks in distribution, got nearly uniform {counts}"
    # ----- GOLD ASSERTION END -----

    print("QFT Gold Assertion Passed.")
    print("Measurement Counts:", counts)
