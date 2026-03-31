import math
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from fractions import Fraction

class ShorPeriodFindingSimple:
    def __init__(self, shots=1024):
        self.n = 3
        self.shots = shots
        self.backend = Aer.get_backend("qasm_simulator")

    def build_faulty_circuit(self):
        qc = QuantumCircuit(self.n, self.n)

        # ❌ Faulty: Prepare uniform superposition
        qc.h(range(self.n-1))
        qc.barrier()

        qc.cz(0, 1)
        qc.cz(1, 2)

        qc.measure(range(self.n), range(self.n))
        return qc

    def run(self):
        qc = self.build_faulty_circuit()
        transpiled = transpile(qc, self.backend)
        job = self.backend.run(transpiled, shots=self.shots)
        result = job.result()
        counts = result.get_counts()

        return counts


if __name__ == "__main__":
    shor = ShorPeriodFindingSimple()
    output = shor.run()
    print("Faulty Shor period finding (expected to fail):", output)
