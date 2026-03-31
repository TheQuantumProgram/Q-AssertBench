from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
import numpy as np

class QuantumStateDistributionCircuit:
    def __init__(self, shots=1024):
        self.shots = shots
        self.circuit = QuantumCircuit(4, 4)
        self.backend = Aer.get_backend("qasm_simulator")

    def build_circuit(self):
        # Set q[0], q[2], q[3] to |1⟩
        self.circuit.x(0)
        self.circuit.x(2)
        self.circuit.x(3)

        # Bias q[1] toward |1⟩ with a strong rotation
        self.circuit.ry(1 * np.pi / 6, 1)

        # Measure all qubits
        self.circuit.measure(range(4), range(4))

    def run(self):
        self.build_circuit()
        transpiled = transpile(self.circuit, self.backend)
        job = self.backend.run(transpiled, shots=self.shots)
        result = job.result()
        counts = result.get_counts()

        # ----- GOLD ASSERTION START -----
        # Check if there exists a state with dominant probability
        dominant_ratio = max(counts.values()) / self.shots
        assert dominant_ratio > 0.8, f"No dominant quantum state found. Max ratio: {dominant_ratio:.3f}"
        # ----- GOLD ASSERTION END -----

        return counts

if __name__ == "__main__":
    circuit_runner = QuantumStateDistributionCircuit()
    output = circuit_runner.run()
    print("Measurement Counts:", output)
