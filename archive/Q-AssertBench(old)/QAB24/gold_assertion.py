from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer


class GroverSearchWithUniformAssertion:
    def __init__(self, shots=1024):
        self.n = 3
        self.shots = shots
        self.backend = Aer.get_backend("qasm_simulator")

    def build_uniform_circuit(self):
        qc = QuantumCircuit(self.n, self.n)

        # Step 1: Superposition
        qc.h(range(self.n))
        qc.barrier()

        # Measure immediately to check uniformity
        qc.measure(range(self.n), range(self.n))
        return qc

    def run(self):
        qc = self.build_uniform_circuit()
        transpiled = transpile(qc, self.backend)
        job = self.backend.run(transpiled, shots=self.shots)
        result = job.result()
        counts = result.get_counts()

        # ----- GOLD ASSERTION START -----
        expected_prob = 1 / (2 ** self.n)
        tolerance = 0.1  # allow ±10%
        for state in [format(i, "03b") for i in range(2 ** self.n)]:
            prob = counts.get(state, 0) / self.shots
            assert abs(prob - expected_prob) < tolerance, (
                f"State {state} deviates too much: {prob:.3f} vs expected {expected_prob:.3f}"
            )
        # ----- GOLD ASSERTION END -----

        return counts


if __name__ == "__main__":
    grover = GroverSearchWithUniformAssertion()
    output = grover.run()
    print("Uniform superposition assertion passed.")
    print("Measurement Counts:", output)
