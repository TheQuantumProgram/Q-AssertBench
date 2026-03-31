from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
import numpy as np

class UniformDistributionCircuit:
    def __init__(self, shots=1024):
        self.shots = shots
        self.circuit = QuantumCircuit(3, 3)
        self.backend = Aer.get_backend("qasm_simulator")

    def build_circuit(self):
        # Faulty: Apply Hadamard only to qubit 0 and 2, omit q[1]
        self.circuit.h(0)
        # self.circuit.h(1)  # <-- Removed on purpose
        self.circuit.h(2)

        # Entanglement (still applied)
        self.circuit.cx(0, 1)
        self.circuit.cx(1, 2)

        # Measurement
        self.circuit.measure(range(3), range(3))

    def run(self):
        self.build_circuit()
        transpiled = transpile(self.circuit, self.backend)
        job = self.backend.run(transpiled, shots=self.shots)
        result = job.result()
        counts = result.get_counts()
        return counts

if __name__ == "__main__":
    circuit_runner = UniformDistributionCircuit()
    output = circuit_runner.run()
    print("Measurement Counts (Faulty):", output)
