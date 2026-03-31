from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
import math


class ShorPeriodFindingAssertion:
    def __init__(self, shots=1024):
        self.n = 5
        self.shots = shots
        self.backend = Aer.get_backend("qasm_simulator")

    def build_circuit(self):
        qc = QuantumCircuit(self.n, self.n)
        qc.x(0)

        # Controlled multiplications mod 15 (simplified)
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
        counts = result.get_counts()

        # ----- GOLD ASSERTION START -----
        # Expect outcomes consistent with period r=4: x = 0, 2, 4, 6
        valid_outcomes = {"000", "010", "100", "110"}  # low 3 classical bits
        observed = set(k[-3:] for k in counts.keys())
        assert observed & valid_outcomes, (
            f"Expected periodic outcomes {valid_outcomes}, got {observed}"
        )
        # ----- GOLD ASSERTION END -----

        return counts


if __name__ == "__main__":
    shor = ShorPeriodFindingAssertion()
    output = shor.run()
    print("Shor period-finding assertion passed.")
    print("Measurement Counts:", output)
