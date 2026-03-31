from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

class SimonsAlgorithmCircuit:
    def __init__(self, shots=1024):
        self.shots = shots
        self.n = 2
        self.a = "11"
        self.backend = Aer.get_backend("qasm_simulator")
        self.circuit = QuantumCircuit(2 * self.n, self.n)

    def apply_oracle(self):
        # ❌ Faulty oracle: missing one CX connection
        self.circuit.cx(0, 2)
        self.circuit.cx(1, 2)
        self.circuit.cx(0, 3)
        # skip cx(1,3)

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
        return counts

if __name__ == "__main__":
    simon_runner = SimonsAlgorithmCircuit()
    output = simon_runner.run()
    print("Measurement Counts:", output)
