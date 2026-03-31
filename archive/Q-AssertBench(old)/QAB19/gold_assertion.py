from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

class SimonsAlgorithmConstraintCheck:
    def __init__(self, shots=1024):
        self.shots = shots
        self.n = 2
        self.a = "11"
        self.backend = Aer.get_backend("qasm_simulator")
        self.circuit = QuantumCircuit(2 * self.n, self.n)

    def apply_oracle(self):
        # Oracle for a = "11"
        self.circuit.cx(0, 2)
        self.circuit.cx(1, 2)
        self.circuit.cx(0, 3)
        self.circuit.cx(1, 3)

    def build_circuit(self):
        for i in range(self.n):
            self.circuit.h(i)
        self.apply_oracle()
        for i in range(self.n):
            self.circuit.h(i)
        for i in range(self.n):
            self.circuit.measure(i, i)

    def run(self):
        self.build_circuit()
        transpiled = transpile(self.circuit, self.backend)
        job = self.backend.run(transpiled, shots=self.shots)
        result = job.result()
        counts = result.get_counts()

        # ----- GOLD ASSERTION START -----
        # For a = "11", valid z must satisfy z0+z1 ≡ 0 (mod 2)
        for z, cnt in counts.items():
            dot = (int(z[0]) * int(self.a[0]) + int(z[1]) * int(self.a[1])) % 2
            assert dot == 0, f"Invalid result {z} violates constraint z·a=0"
        # ----- GOLD ASSERTION END -----

        return counts

if __name__ == "__main__":
    checker = SimonsAlgorithmConstraintCheck()
    output = checker.run()
    print("Constraint Test, Measurement Counts:", output)
