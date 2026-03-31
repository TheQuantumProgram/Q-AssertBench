import math
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer


class ShorPeriodFinding:
    def __init__(self, shots=1024):
        self.n = 5
        self.shots = shots
        self.backend = Aer.get_backend("qasm_simulator")

    def build_faulty_circuit(self):
        qc = QuantumCircuit(self.n, self.n)
        qc.x(0)

        qc.h(4)
        qc.h(4)
        qc.measure(4, 0)
        qc.reset(4)

        qc.h(4)
        qc.cx(4, 2)
        qc.cx(4, 0)
        qc.h(4)
        qc.measure(4, 1)
        qc.reset(4)

        qc.h(4)
        # ❌ Faulty: skip some cswap operations
        qc.cswap(4, 3, 2)
        # missing qc.cswap(4, 2, 1)
        # missing qc.cswap(4, 1, 0)
        qc.h(4)
        qc.measure(4, 2)

        return qc

    def run(self):
        qc = self.build_faulty_circuit()
        transpiled = transpile(qc, self.backend)
        job = self.backend.run(transpiled, shots=self.shots)
        result = job.result()
        return result.get_counts()


if __name__ == "__main__":
    shor = ShorPeriodFinding()
    output = shor.run()
    print("Faulty Shor period finding result:", output)
