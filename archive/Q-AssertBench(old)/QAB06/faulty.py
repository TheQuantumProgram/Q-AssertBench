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

        # Faulty: Use weaker rotation → probability of q[1] = 1 is lower
        self.circuit.ry(np.pi / 2, 1)  # Previously was 5π/6

        # Measure all qubits
        self.circuit.measure(range(4), range(4))

    def run(self):
        self.build_circuit()
        transpiled = transpile(self.circuit, self.backend)
        job = self.backend.run(transpiled, shots=self.shots)
        result = job.result()
        counts = result.get_counts()
        return counts

if __name__ == "__main__":
    circuit_runner = QuantumStateDistributionCircuit()
    output = circuit_runner.run()
    print("Measurement Counts (Faulty):", output)
