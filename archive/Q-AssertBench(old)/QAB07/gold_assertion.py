from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

class UniformDistributionCircuit:
    def __init__(self, shots=1024):
        self.shots = shots
        self.circuit = QuantumCircuit(3, 3)
        self.backend = Aer.get_backend("qasm_simulator")

    def build_circuit(self):
        # Step 1: Create superposition on all qubits
        self.circuit.h(0)
        self.circuit.h(1)
        self.circuit.h(2)

        # Step 2: Add light entanglement
        self.circuit.cx(0, 1)
        self.circuit.cx(1, 2)

        # Step 3: Measurement
        self.circuit.measure(range(3), range(3))

    def run(self):
        self.build_circuit()
        transpiled = transpile(self.circuit, self.backend)
        job = self.backend.run(transpiled, shots=self.shots)
        result = job.result()
        counts = result.get_counts()

        # ----- GOLD ASSERTION START -----
        # Assert that the output distribution is approximately uniform
        probs = [count / self.shots for count in counts.values()]
        assert max(probs) - min(probs) < 0.1, f"Distribution not uniform enough: max-min = {max(probs) - min(probs):.3f}"
        # ----- GOLD ASSERTION END -----

        return counts

if __name__ == "__main__":
    circuit_runner = UniformDistributionCircuit()
    output = circuit_runner.run()
    print("Measurement Counts:", output)
