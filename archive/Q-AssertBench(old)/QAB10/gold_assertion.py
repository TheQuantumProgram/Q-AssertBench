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

        # Step 2: Cascade entanglement to other qubits (GHZ construction)
        self.circuit.cx(0, 1)
        self.circuit.cx(1, 2)
        self.circuit.cx(2, 3)

        # Step 3: Measurement
        self.circuit.measure(range(4), range(4))

    def run(self):
        self.build_circuit()
        transpiled = transpile(self.circuit, self.backend)
        job = self.backend.run(transpiled, shots=self.shots)
        result = job.result()
        counts = result.get_counts()

        # ----- GOLD ASSERTION START -----
        # Ensure that only '0000' and '1111' dominate the measurement results
        valid_ratio = sum(v for k, v in counts.items() if k in ["0000", "1111"]) / self.shots
        assert valid_ratio > 0.9, f"Unexpected states found: {counts}"
        # ----- GOLD ASSERTION END -----

        return counts

if __name__ == "__main__":
    circuit_runner = GHZEntanglementCircuit()
    output = circuit_runner.run()
    print("Measurement Counts:", output)
