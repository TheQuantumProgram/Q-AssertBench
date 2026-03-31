from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

class DeutschAlgorithmCircuit:
    def __init__(self, shots=1024):
        self.shots = shots
        # 2 qubits, but only 1 classical bit is needed (for q0)
        self.circuit = QuantumCircuit(2, 1)
        self.backend = Aer.get_backend("qasm_simulator")

    def build_circuit(self):
        # Step 1: Initialize ancilla qubit q1 in |1⟩
        self.circuit.x(1)

        # Step 2: Prepare superposition
        self.circuit.h(0)
        self.circuit.h(1)

        # Step 3: Oracle for f(x) = x (balanced function)
        self.circuit.cx(0, 1)

        # Step 4: Apply Hadamard gates again
        self.circuit.h(0)
        self.circuit.h(1)

        # Step 5: Measure only the first qubit (decision qubit)
        self.circuit.measure(0, 0)

    def run(self):
        self.build_circuit()
        transpiled = transpile(self.circuit, self.backend)
        job = self.backend.run(transpiled, shots=self.shots)
        result = job.result()
        counts = result.get_counts()

        # ----- GOLD ASSERTION START -----
        # Deutsch Algorithm Decision Rule:
        # - If f(x) is CONSTANT -> q0 always measured as 0
        # - If f(x) is BALANCED -> q0 always measured as 1
        #
        # Our oracle implements f(x) = x, which is BALANCED.
        # Therefore, we expect nearly all measurement results to be '1'.
        assert "1" in counts and counts["1"] > 0.9 * self.shots, (
            f"Expected balanced function outcome (q0=1), but got counts = {counts}"
        )
        # ----- GOLD ASSERTION END -----

        return counts

if __name__ == "__main__":
    circuit_runner = DeutschAlgorithmCircuit()
    output = circuit_runner.run()
    print("Measurement Counts:", output)