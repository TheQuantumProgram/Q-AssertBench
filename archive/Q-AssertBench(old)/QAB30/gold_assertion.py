from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import numpy as np


class ShorLargeCircuit:
    def __init__(self, N=15, a=7, shots=1024):
        self.N = N
        self.a = a
        self.n_count = 8
        self.work_qubits = 7
        self.total_qubits = self.n_count + self.work_qubits
        self.backend = AerSimulator()
        self.shots = shots
        self.circuit = None
        self.counts = None

    def build_circuit(self):
        qc = QuantumCircuit(self.total_qubits, self.n_count)

        for q in range(self.n_count):
            qc.h(q)

        for j in range(self.n_count):
            for k in range(self.work_qubits):
                qc.cx(j, self.n_count + k)

        # Inverse QFT
        for j in range(self.n_count // 2):
            qc.swap(j, self.n_count - j - 1)

        for j in range(self.n_count):
            qc.h(j)
            for k in range(j + 1, self.n_count):
                angle = -np.pi / (2 ** (k - j))
                qc.cp(angle, k, j)

        for i in range(self.n_count):
            qc.measure(i, i)

        self.circuit = qc

    def run(self):
        self.build_circuit()
        compiled = transpile(self.circuit, self.backend)
        job = self.backend.run(compiled, shots=self.shots)
        result = job.result()
        self.counts = result.get_counts()

        # ----- GOLD ASSERTION START -----
        sorted_counts = sorted(self.counts.items(), key=lambda x: -x[1])
        topk = 3
        topk_total = sum(v for _, v in sorted_counts[:topk])
        total = sum(self.counts.values())
        ratio = topk_total / total
        print(f"[GOLD ASSERTION] Top-{topk} states carry {ratio:.3f} of probability mass")
        assert ratio > 0.1, (
            f"Expected top-{topk} peaks to dominate (>10%), but got {ratio:.3f}"
        )
        # ----- GOLD ASSERTION END -----

        return self.counts


if __name__ == "__main__":
    program = ShorLargeCircuit()
    result = program.run()
    print("Measurement Results:")
    for b, c in result.items():
        print(f"{b}: {c}")
