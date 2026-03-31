from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
import numpy as np

class PauliGatesCircuit:
    def __init__(self, shots=1024):
        self.shots = shots
        self.circuit = QuantumCircuit(1, 1)
        self.backend = Aer.get_backend("qasm_simulator")

    def build_circuit(self):

        #self.circuit.rx(np.pi / 2, 0)

        self.circuit.ry(2 * np.pi / 3, 0)

        self.circuit.z(0)

        self.circuit.measure(0, 0)

    def run(self):
        self.build_circuit()
        transpiled = transpile(self.circuit, self.backend)
        job = self.backend.run(transpiled, shots=self.shots)
        result = job.result()
        counts = result.get_counts()

        # ----- GOLD ASSERTION START -----
        # Compute the probability of measuring '1' and assert it's approximately 0.75
        p1 = counts.get("1", 0) / self.shots
        assert abs(p1 - 0.75) < 0.05, f"Assertion failed: P(1) = {p1:.3f}, expected ≈ 0.75"
        # ----- GOLD ASSERTION END -----

        return counts

if __name__ == "__main__":
    circuit_runner = PauliGatesCircuit()
    output = circuit_runner.run()
    print("Measurement Counts:", output)
