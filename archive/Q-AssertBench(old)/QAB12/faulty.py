from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

class DeutschAlgorithmCircuit:
    def __init__(self, oracle_type=0, shots=1024):
        """
        Faulty version:
        Even if oracle_type=0 (constant), the oracle is implemented incorrectly as balanced.
        This inconsistency will cause the assertion to fail.
        """
        self.oracle_type = oracle_type
        self.shots = shots
        self.circuit = QuantumCircuit(2, 1)  # 2 qubits, 1 classical bit
        self.backend = Aer.get_backend("qasm_simulator")

    def apply_oracle(self):
        if self.oracle_type == 0:
            # ❌ Faulty: instead of doing nothing, apply CX (balanced function)
            self.circuit.cx(0, 1)
        elif self.oracle_type == 1:
            # Balanced function f(x) = x (this part is correct)
            self.circuit.cx(0, 1)
        else:
            raise ValueError("oracle_type must be 0 or 1")

    def build_circuit(self):
        # Step 1: Initialize ancilla qubit q1 in |1⟩
        self.circuit.x(1)

        # Step 2: Apply Hadamard gates
        self.circuit.h(0)
        self.circuit.h(1)

        # Step 3: Oracle
        self.apply_oracle()

        # Step 4: Apply Hadamard to the first qubit
        self.circuit.h(0)

        # Step 5: Measure the first qubit
        self.circuit.measure(0, 0)

    def run(self):
        self.build_circuit()
        transpiled = transpile(self.circuit, self.backend)
        job = self.backend.run(transpiled, shots=self.shots)
        result = job.result()
        counts = result.get_counts()
        return counts

if __name__ == "__main__":
    for oracle_type in [0, 1]:
        circuit_runner = DeutschAlgorithmCircuit(oracle_type=oracle_type)
        output = circuit_runner.run()
        print(f"Faulty Oracle type {oracle_type}, Measurement Counts:", output)
