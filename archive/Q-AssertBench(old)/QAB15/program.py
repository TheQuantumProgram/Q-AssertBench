from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

class BernsteinVaziraniCircuit:
    def __init__(self, a="111", shots=1024):
        """
        Bernstein-Vazirani Algorithm
        a: hidden string (binary as str, e.g. "111" or "101")
        """
        self.a = a
        self.n = len(a)  # number of input qubits
        self.shots = shots
        self.circuit = QuantumCircuit(self.n + 1, self.n)  # n input + 1 ancilla, measure only n
        self.backend = Aer.get_backend("qasm_simulator")

    def apply_oracle(self):
        # Oracle for f(x) = a · x mod 2
        for i, bit in enumerate(self.a):
            if bit == "1":
                self.circuit.cx(i, self.n)  # control: input qubit, target: ancilla

    def build_circuit(self):
        # Step 1: Initialize ancilla qubit in |1⟩
        self.circuit.x(self.n)

        # Step 2: Apply Hadamard to all qubits (prepare uniform superposition)
        for i in range(self.n + 1):
            self.circuit.h(i)

        # Step 3: Apply oracle
        self.apply_oracle()

        # Step 4: Apply Hadamard to input qubits
        for i in range(self.n):
            self.circuit.h(i)

        # Step 5: Measure only the input qubits
        for i in range(self.n):
            self.circuit.measure(i, i)

    def run(self):
        self.build_circuit()
        transpiled = transpile(self.circuit, self.backend)
        job = self.backend.run(transpiled, shots=self.shots)
        result = job.result()
        counts = result.get_counts()
        return counts

if __name__ == "__main__":
    # Example with a = "111"
    circuit_runner = BernsteinVaziraniCircuit(a="111")
    output = circuit_runner.run()
    print("Measurement Counts:", output)
