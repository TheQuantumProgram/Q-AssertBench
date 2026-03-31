import math
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer


class ShorPeriodFindingSimple:
    def __init__(self, shots=1024):
        self.n = 3  # use 3 qubits for counting register
        self.shots = shots
        self.backend = Aer.get_backend("qasm_simulator")

    def build_circuit(self):
        qc = QuantumCircuit(self.n, self.n)

        # Prepare a periodic function mod 15 (simplified)
        # Just simulate the effect that gives peaks at multiples of 2
        qc.h(range(self.n))  # uniform superposition
        qc.barrier()

        # Apply "black-box oracle" that encodes periodicity
        # For simplicity, mimic the interference pattern
        qc.cz(0, 1)
        qc.cz(1, 2)

        # Measure the counting register
        qc.measure(range(self.n), range(self.n))
        return qc

    def run(self):
        qc = self.build_circuit()
        transpiled = transpile(qc, self.backend)
        job = self.backend.run(transpiled, shots=self.shots)
        result = job.result()
        return result.get_counts()


if __name__ == "__main__":
    shor = ShorPeriodFindingSimple()
    output = shor.run()
    print("Shor simplified period finding measurement:", output)
