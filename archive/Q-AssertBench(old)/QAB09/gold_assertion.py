from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

class EntanglementDetectionCircuit:
    def __init__(self, shots=1024):
        self.shots = shots
        self.circuit = QuantumCircuit(2, 2)
        self.backend = Aer.get_backend("qasm_simulator")

    def build_circuit(self):
        # Step 1: Put q0 in superposition
        self.circuit.h(0)

        # Step 2: Entangle q0 and q1
        self.circuit.cx(0, 1)

        # Step 3: Measurement
        self.circuit.measure([0, 1], [0, 1])

    def run(self):
        self.build_circuit()
        transpiled = transpile(self.circuit, self.backend)
        job = self.backend.run(transpiled, shots=self.shots)
        result = job.result()
        counts = result.get_counts()

        # ----- GOLD ASSERTION START -----
        # Compute marginal and joint probabilities
        p_q0_1 = sum(v for k, v in counts.items() if k[0] == "1") / self.shots
        p_q1_1 = sum(v for k, v in counts.items() if k[1] == "1") / self.shots
        p_q0q1_11 = counts.get("11", 0) / self.shots

        # Difference between observed joint and independent expectation
        expected_independent = p_q0_1 * p_q1_1
        diff = abs(p_q0q1_11 - expected_independent)

        # Assert strong correlation (positive or negative)
        assert diff > 0.1, (
            f"No strong correlation detected: "
            f"joint={p_q0q1_11:.3f}, independent={expected_independent:.3f}, diff={diff:.3f}"
        )
        # ----- GOLD ASSERTION END -----

        return counts

if __name__ == "__main__":
    circuit_runner = EntanglementDetectionCircuit()
    output = circuit_runner.run()
    print("Measurement Counts:", output)
