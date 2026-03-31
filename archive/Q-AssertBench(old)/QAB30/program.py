from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import numpy as np


class ShorLargeCircuit:
    """
    QAB-30: Shor's Algorithm Benchmark with 15 Qubits.
    This version emphasizes circuit width and depth.
    Modular exponentiation is abstracted for benchmarking.
    """

    def __init__(self, N=15, a=7, shots=1024):
        self.N = N
        self.a = a
        self.n_count = 8           # Counting qubits
        self.work_qubits = 7       # Work/ancilla register
        self.total_qubits = self.n_count + self.work_qubits
        self.backend = AerSimulator()
        self.shots = shots
        self.circuit = None
        self.counts = None

    def build_circuit(self):
        qc = QuantumCircuit(self.total_qubits, self.n_count)

        # Step 1: Hadamard on counting register
        for q in range(self.n_count):
            qc.h(q)

        # Step 2: Fake modular exponentiation
        # Entangle counting qubits with work qubits
        for j in range(self.n_count):
            for k in range(self.work_qubits):
                qc.cx(j, self.n_count + k)

        # Step 3: Inverse QFT on counting register
        for j in range(self.n_count // 2):
            qc.swap(j, self.n_count - j - 1)

        for j in range(self.n_count):
            qc.h(j)
            for k in range(j + 1, self.n_count):
                angle = -np.pi / (2 ** (k - j))
                qc.cp(angle, k, j)

        # Step 4: Measure counting qubits
        for i in range(self.n_count):
            qc.measure(i, i)

        self.circuit = qc

    def run(self):
        self.build_circuit()
        compiled = transpile(self.circuit, self.backend)
        job = self.backend.run(compiled, shots=self.shots)
        result = job.result()
        self.counts = result.get_counts()
        return self.counts


if __name__ == "__main__":
    program = ShorLargeCircuit()
    result = program.run()
    print("Measurement Results:")
    for bitstring, count in result.items():
        print(f"{bitstring}: {count}")
