from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

class GHZEntanglementCircuit:
    def __init__(self, shots=1024):
        self.shots = shots
        self.circuit = QuantumCircuit(4, 4)
        self.backend = Aer.get_backend("qasm_simulator")

    def build_circuit(self):
        # Step 1: Put q0 into superposition
        self.circuit.h(0)

        # Step 2: Incorrect entanglement (last CX reversed)
        self.circuit.cx(0, 1)
        self.circuit.cx(1, 2)
        self.circuit.cx(3, 2)  # ❌ faulty: should be cx(2, 3)

        # Step 3: Measurement
        self.circuit.measure(range(4), range(4))

    def run(self):
        self.build_circuit()
        transpiled = transpile(self.circuit, self.backend)
        job = self.backend.run(transpiled, shots=self.shots)
        result = job.result()
        counts = result.get_counts()
        return counts

if __name__ == "__main__":
    circuit_runner = GHZEntanglementCircuit()
    output = circuit_runner.run()
    print("Measurement Counts (Faulty):", output)
