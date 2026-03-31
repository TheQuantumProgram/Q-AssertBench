from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

class SimonsAlgorithmPairCheck:
    def __init__(self, shots=1024):
        self.shots = shots
        self.n = 2
        self.a = "11"
        self.backend = Aer.get_backend("qasm_simulator")

    def apply_oracle(self, circuit):
        # Oracle for a = "11"
        circuit.cx(0, 2)
        circuit.cx(1, 2)
        circuit.cx(0, 3)
        circuit.cx(1, 3)

    def build_circuit(self):
        circuit = QuantumCircuit(2 * self.n, 2 * self.n)
        # Step 1: Hadamard on input
        for i in range(self.n):
            circuit.h(i)
        # Step 2: Oracle
        self.apply_oracle(circuit)
        # Step 3: Measure output
        for i in range(self.n):
            circuit.measure(i + self.n, i + self.n)
        # Step 4: Measure input
        for i in range(self.n):
            circuit.measure(i, i)
        return circuit

    def run(self):
        circuit = self.build_circuit()
        transpiled = transpile(circuit, self.backend)
        job = self.backend.run(transpiled, shots=self.shots)
        result = job.result()
        counts = result.get_counts()

        # ----- GOLD ASSERTION START -----
        # Check that input results occur in pairs x and x⊕a
        def xor_strings(s1, s2):
            return "".join(str(int(b1) ^ int(b2)) for b1, b2 in zip(s1, s2))

        input_counts = {}
        for bitstring, cnt in counts.items():
            x = bitstring[-self.n:]  # input part
            input_counts[x] = input_counts.get(x, 0) + cnt

        for x in input_counts:
            x_pair = xor_strings(x, self.a)
            if x_pair in input_counts:
                continue
            else:
                raise AssertionError(f"Input {x} did not appear with its pair {x_pair}")
        # ----- GOLD ASSERTION END -----

        return counts

if __name__ == "__main__":
    checker = SimonsAlgorithmPairCheck()
    output = checker.run()
    print("Pairwise Structure Test, Measurement Counts:", output)
