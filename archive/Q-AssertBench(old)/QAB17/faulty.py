from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

class SimonsAlgorithmCircuit:
    def __init__(self, shots=1024):
        """
        Faulty version of Simon's Algorithm.
        Only applies Hadamard to one input qubit instead of both.
        """
        self.shots = shots
        self.n = 2
        self.a = "11"
        self.circuit = QuantumCircuit(2 * self.n, self.n)  # measure only input register
        self.backend = Aer.get_backend("qasm_simulator")

    def apply_oracle(self):
        # Oracle for a = "11"
        self.circuit.cx(0, 2)
        self.circuit.cx(1, 2)
        self.circuit.cx(0, 3)
        self.circuit.cx(1, 3)

    def build_circuit(self):
        # Step 1: Faulty Hadamard (only on first input qubit)
        self.circuit.h(0)  # ❌ should apply to both 0 and 1

        # Step 2: Oracle
        self.apply_oracle()

        # Step 3: Hadamard on input again (both correct)
        for i in range(self.n):
            self.circuit.h(i)

        # Step 4: Measure input qubits only
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
    simon_runner = SimonsAlgorithmCircuit()
    output = simon_runner.run()
    print("Measurement Counts:", output)
