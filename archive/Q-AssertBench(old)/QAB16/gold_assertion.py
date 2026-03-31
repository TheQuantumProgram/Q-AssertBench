from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

class BernsteinVaziraniCircuit:
    def __init__(self, a="111", shots=1024):
        self.a = a
        self.n = len(a)
        self.shots = shots
        self.backend = Aer.get_backend("qasm_simulator")
        self.circuit = QuantumCircuit(self.n + 1, self.n)

    def apply_oracle(self):
        for i, bit in enumerate(self.a):
            if bit == "1":
                self.circuit.cx(i, self.n)

    def build_circuit(self):
        self.circuit.x(self.n)
        for i in range(self.n + 1):
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
        # The final measurement should reveal the hidden string a
        assert self.a in counts and counts[self.a] > 0.9 * self.shots, (
            f"Expected outcome {self.a}, but got {counts}"
        )
        # ----- GOLD ASSERTION END -----

        return counts

if __name__ == "__main__":
    circuit_runner = BernsteinVaziraniCircuit(a="111")
    output = circuit_runner.run()
    print("Measurement Counts:", output)
