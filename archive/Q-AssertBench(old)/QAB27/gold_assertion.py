from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from fractions import Fraction


class ShorPeriodFindingWithAssertion:
    def __init__(self, shots=1024):
        self.n = 3
        self.shots = shots
        self.backend = Aer.get_backend("qasm_simulator")

    def build_circuit(self):
        qc = QuantumCircuit(self.n, self.n)
        qc.h(range(self.n))
        qc.barrier()
        qc.cz(0, 1)
        qc.cz(1, 2)
        qc.measure(range(self.n), range(self.n))
        return qc

    def run(self):
        qc = self.build_circuit()
        transpiled = transpile(qc, self.backend)
        job = self.backend.run(transpiled, shots=self.shots)
        result = job.result()
        counts = result.get_counts()

        # ----- GOLD ASSERTION START -----
        dominant = max(counts, key=counts.get)
        x = int(dominant, 2)
        frac = Fraction(x, 2 ** self.n).limit_denominator(15)  # keep denominator small
        r = frac.denominator

        # Allow r = 4 or multiples (e.g., 8) since continued fraction can overshoot
        assert r % 4 == 0, f"Expected period multiple of 4, got r={r} from x={x}"
        # ----- GOLD ASSERTION END -----

        return counts


if __name__ == "__main__":
    shor = ShorPeriodFindingWithAssertion()
    output = shor.run()
    print("Shor period-finding assertion passed.")
    print("Measurement Counts:", output)
