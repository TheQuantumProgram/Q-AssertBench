from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

class DeutschAlgorithmCircuit:
    def __init__(self, oracle_type=0, shots=1024):
        """
        oracle_type = 0 → constant function (f(x) = 0)
        oracle_type = 1 → balanced function (f(x) = x)
        """
        self.oracle_type = oracle_type
        self.shots = shots
        self.circuit = QuantumCircuit(2, 1)  # 2 qubits, 1 classical bit
        self.backend = Aer.get_backend("qasm_simulator")

    def apply_oracle(self):
        if self.oracle_type == 0:
            # Constant function f(x)=0 → do nothing
            pass
        elif self.oracle_type == 1:
            # Balanced function f(x)=x → CX(q0, q1)
            self.circuit.cx(0, 1)
        else:
            raise ValueError("oracle_type must be 0 or 1")

    def build_circuit(self):
        # Step 1: Initialize ancilla qubit q1 in |1⟩
        self.circuit.x(1)

        # Step 2: Apply Hadamard gates to both qubits
        self.circuit.h(0)
        self.circuit.h(1)

        # Step 3: Oracle
        self.apply_oracle()

        # Step 4: Apply Hadamard again to the first qubit
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
    # Example: try both oracle types
    for oracle_type in [0, 1]:
        circuit_runner = DeutschAlgorithmCircuit(oracle_type=oracle_type)
        output = circuit_runner.run()
        print(f"Oracle type {oracle_type}, Measurement Counts:", output)
