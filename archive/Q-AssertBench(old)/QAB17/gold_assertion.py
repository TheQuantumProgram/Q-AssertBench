from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

class SimonsAlgorithmUniformCheck:
    def __init__(self, n=2, shots=1024):
        self.n = n
        self.shots = shots
        self.backend = Aer.get_backend("qasm_simulator")

    def build_uniform_superposition(self):
        circuit = QuantumCircuit(self.n, self.n)
        for i in range(self.n):
            circuit.h(i)
        for i in range(self.n):
            circuit.measure(i, i)
        return circuit

    def run(self):
        circuit = self.build_uniform_superposition()
        transpiled = transpile(circuit, self.backend)
        job = self.backend.run(transpiled, shots=self.shots)
        result = job.result()
        counts = result.get_counts()

        # ----- GOLD ASSERTION START -----
        expected_prob = 1 / (2**self.n)
        tolerance = 0.15
        for state in [format(i, f"0{self.n}b") for i in range(2**self.n)]:
            prob = counts.get(state, 0) / self.shots
            assert abs(prob - expected_prob) < tolerance, (
                f"State {state} has probability {prob:.3f}, expected ~{expected_prob:.3f}"
            )
        # ----- GOLD ASSERTION END -----

        return counts

if __name__ == "__main__":
    checker = SimonsAlgorithmUniformCheck()
    output = checker.run()
    print("Uniform Superposition Test, Measurement Counts:", output)
