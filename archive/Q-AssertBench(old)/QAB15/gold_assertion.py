from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

class BernsteinVaziraniCircuit:
    def __init__(self, a="111", shots=1024):
        """
        Bernstein-Vazirani Algorithm
        Assertion: check that uniform superposition is correctly prepared.
        """
        self.a = a
        self.n = len(a)
        self.shots = shots
        self.backend = Aer.get_backend("qasm_simulator")

    def build_uniform_superposition(self):
        circuit = QuantumCircuit(self.n, self.n)  # only input qubits (ignore ancilla for this check)

        # Prepare |0^n>
        # Apply Hadamards to all input qubits
        for i in range(self.n):
            circuit.h(i)

        # Add measurement
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
        # Expect uniform distribution across all 2^n states
        expected_prob = 1 / (2**self.n)
        tolerance = 0.1  # allow ~10% deviation

        for state in [format(i, f"0{self.n}b") for i in range(2**self.n)]:
            prob = counts.get(state, 0) / self.shots
            assert abs(prob - expected_prob) < tolerance, (
                f"State {state} has probability {prob:.3f}, expected ~{expected_prob:.3f}"
            )
        # ----- GOLD ASSERTION END -----

        return counts

if __name__ == "__main__":
    circuit_runner = BernsteinVaziraniCircuit(a="111")
    output = circuit_runner.run()
    print("Uniform Superposition Test, Measurement Counts:", output)
