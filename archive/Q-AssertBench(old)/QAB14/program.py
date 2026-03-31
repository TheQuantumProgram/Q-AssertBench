from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

class DeutschJozsaCircuit:
    def __init__(self, oracle_type=0, shots=1024):
        """
        Deutsch–Jozsa Algorithm with configurable oracle.

        oracle_type = 0 → constant function f(x)=0
        oracle_type = 1 → balanced function f(x0, x1) = x0 XOR x1
        """
        self.oracle_type = oracle_type
        self.shots = shots
        self.circuit = QuantumCircuit(3, 2)  # 2 input qubits + 1 ancilla, 2 classical bits
        self.backend = Aer.get_backend("qasm_simulator")

    def apply_oracle(self):
        if self.oracle_type == 0:
            # Constant oracle f(x)=0 → do nothing
            pass
        elif self.oracle_type == 1:
            # Balanced oracle f(x0, x1) = x0 XOR x1
            self.circuit.cx(0, 2)
            self.circuit.cx(1, 2)
        else:
            raise ValueError("oracle_type must be 0 or 1")

    def build_circuit(self):
        # Step 1: Initialize ancilla qubit in |1⟩
        self.circuit.x(2)

        # Step 2: Apply Hadamard to all qubits
        for i in range(3):
            self.circuit.h(i)

        # Step 3: Oracle
        self.apply_oracle()

        # Step 4: Apply Hadamard to input qubits
        self.circuit.h(0)
        self.circuit.h(1)

        # Step 5: Measure input qubits
        self.circuit.measure(0, 0)
        self.circuit.measure(1, 1)

    def run(self):
        self.build_circuit()
        transpiled = transpile(self.circuit, self.backend)
        job = self.backend.run(transpiled, shots=self.shots)
        result = job.result()
        counts = result.get_counts()
        return counts

if __name__ == "__main__":
    for oracle_type in [0, 1]:
        circuit_runner = DeutschJozsaCircuit(oracle_type=oracle_type)
        output = circuit_runner.run()
        print(f"Oracle type {oracle_type}, Measurement Counts:", output)
