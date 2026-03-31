import math
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer


class ShorPeriodFinding:
    def __init__(self, shots=1024):
        self.n = 5
        self.shots = shots
        self.backend = Aer.get_backend("qasm_simulator")

    def build_circuit(self):
        qr_n = self.n
        qc = QuantumCircuit(qr_n, qr_n)

        # Initialize q[0] to |1>
        qc.x(0)

        # Controlled operations approximating a^x mod 15 with a=2
        # Apply a**4 mod 15
        qc.h(4)
        qc.h(4)
        qc.measure(4, 0)
        qc.reset(4)

        # Apply a**2 mod 15
        qc.h(4)
        qc.cx(4, 2)
        qc.cx(4, 0)
        qc.h(4)
        qc.measure(4, 1)
        qc.reset(4)

        # Apply a mod 15
        qc.h(4)
        qc.cswap(4, 3, 2)
        qc.cswap(4, 2, 1)
        qc.cswap(4, 1, 0)
        qc.h(4)
        qc.measure(4, 2)

        return qc

    def run(self):
        qc = self.build_circuit()
        transpiled = transpile(qc, self.backend)
        job = self.backend.run(transpiled, shots=self.shots)
        result = job.result()
        return result.get_counts()


if __name__ == "__main__":
    shor = ShorPeriodFinding()
    output = shor.run()
    print("Shor's period finding result:", output)
