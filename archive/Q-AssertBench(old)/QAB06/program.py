from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
import numpy as np

class QuantumStateDistributionCircuit:
    def __init__(self, shots=1024):
        self.shots = shots
        self.circuit = QuantumCircuit(4, 4)
        self.backend = Aer.get_backend("qasm_simulator")

    def build_circuit(self):
        # Set q[0], q[2], q[3] to |1⟩ using X gates → binary: 1x1x1 (positions: 3 2 1 0)
        self.circuit.x(0)
        self.circuit.x(2)
        self.circuit.x(3)

        # Rotate q[1] toward |1⟩ → controls probability of full 1101 state
        self.circuit.ry(1 * np.pi / 6, 1)

        # Measurement
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
    print("Measurement Counts:", output)
