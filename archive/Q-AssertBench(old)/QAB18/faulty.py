from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

class SimonsAlgorithmCircuit:
    def __init__(self, shots=1024):
        """
        Faulty Simon's Algorithm:
        Oracle is missing some CX gates, leading to incorrect pairwise output structure.
        """
        self.shots = shots
        self.n = 2
        self.a = "11"
        self.circuit = QuantumCircuit(2 * self.n, self.n)  # same structure as program.py
        self.backend = Aer.get_backend("qasm_simulator")

    def apply_oracle(self):
        # ❌ Faulty oracle: missing a connection to qubit 3
        self.circuit.cx(0, 2)
        self.circuit.cx(1, 2)
        #self.circuit.cx(0, 3)  # Missing
        self.circuit.cx(1, 3)

    def build_circuit(self):
        # Step 1: Hadamard on input register
        for i in range(self.n):
            self.circuit.h(i)

        # Step 2: Faulty Oracle
        self.apply_oracle()

        # Step 3: Hadamard again on input
        for i in range(self.n):
            self.circuit.h(i)

        # Step 4: Measure input register only
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
    print("Faulty Oracle Measurement Counts:", output)
