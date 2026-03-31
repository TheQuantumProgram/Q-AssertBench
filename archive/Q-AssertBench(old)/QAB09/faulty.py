from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

class EntanglementDetectionCircuit:
    def __init__(self, shots=1024):
        self.shots = shots
        self.circuit = QuantumCircuit(2, 2)
        self.backend = Aer.get_backend("qasm_simulator")

    def build_circuit(self):
        # Faulty: Put q0 in superposition, but remove entanglement
        self.circuit.h(0)

        # ❌ Missing CX(0, 1) — no entanglement created

        # Measurement
        self.circuit.measure([0, 1], [0, 1])

    def run(self):
        self.build_circuit()
        transpiled = transpile(self.circuit, self.backend)
        job = self.backend.run(transpiled, shots=self.shots)
        result = job.result()
        counts = result.get_counts()
        return counts

if __name__ == "__main__":
    circuit_runner = EntanglementDetectionCircuit()
    output = circuit_runner.run()
    print("Measurement Counts (Faulty):", output)
