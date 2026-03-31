from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
import math


class QuantumFourierTransformWithInverse:
    def __init__(self, n=3, shots=1024):
        self.n = n
        self.shots = shots
        self.backend = Aer.get_backend("qasm_simulator")

    def apply_qft(self, circuit):
        for j in range(self.n):
            circuit.h(j)
            for k in range(j + 1, self.n):
                angle = math.pi / float(2 ** (k - j))
                circuit.cp(angle, k, j)
        circuit.barrier()

    def apply_qft_dagger(self, circuit):
        for j in range(self.n):
            k = (self.n - 1) - j
            for m in range(k):
                angle = -math.pi / float(2 ** (k - m))
                circuit.cp(angle, k, m)
            circuit.h(k)
        circuit.barrier()

    def build_and_run(self, prepare_input=None):
        circuit = QuantumCircuit(self.n, self.n)

        if prepare_input:
            prepare_input(circuit)

        self.apply_qft(circuit)
        self.apply_qft_dagger(circuit)

        circuit.measure(range(self.n), range(self.n))

        transpiled = transpile(circuit, self.backend)
        job = self.backend.run(transpiled, shots=self.shots)
        result = job.result()
        return result.get_counts()


if __name__ == "__main__":
    qft_runner = QuantumFourierTransformWithInverse(n=3, shots=1024)

    def prepare_input(circuit):
        circuit.x(0)
        circuit.x(2)  # prepare |101>

    counts = qft_runner.build_and_run(prepare_input=prepare_input)

    # ----- GOLD ASSERTION START -----
    expected_state = "101"
    dominant = max(counts, key=counts.get)
    dominant_prob = counts[dominant] / qft_runner.shots

    assert dominant == expected_state and dominant_prob > 0.4, (
        f"Expected {expected_state} to dominate (>40%), got {counts}"
    )
    # ----- GOLD ASSERTION END -----

    print("QFT followed by QFT† assertion passed.")
    print("Measurement Counts:", counts)
