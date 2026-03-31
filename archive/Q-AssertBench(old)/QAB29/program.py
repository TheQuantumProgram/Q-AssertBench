from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import numpy as np


class QFTProgram:
    """
    QAB-29 Benchmark Program (10-qubit QFT on periodic input)
    """

    def __init__(self, num_qubits=10, shots=2048, plot=True, period=4):
        self.num_qubits = num_qubits
        self.shots = shots
        self.plot = plot
        self.period = period
        self.backend = AerSimulator()
        self.circuit = None
        self.counts = None

    def prepare_periodic_input(self, qc):
        """
        Prepare superposition of basis states with a given period.
        E.g., for period=4 and n=10 → |0⟩ + |4⟩ + |8⟩ + ... + |1020⟩
        """
        n = self.num_qubits
        state_indexes = list(range(0, 2**n, self.period))
        amp = 1 / np.sqrt(len(state_indexes))

        # Build statevector
        statevector = np.zeros(2**n, dtype=complex)
        for i in state_indexes:
            statevector[i] = amp

        # Initialize from statevector
        from qiskit.quantum_info import Statevector
        qc.initialize(Statevector(statevector).data)

    def apply_qft(self, qc, n):
        for j in range(n):
            qc.h(j)
            for k in range(j + 1, n):
                angle = np.pi / (2 ** (k - j))
                qc.cp(angle, k, j)
        for i in range(n // 2):
            qc.swap(i, n - i - 1)

    def build_circuit(self):
        qc = QuantumCircuit(self.num_qubits)
        self.prepare_periodic_input(qc)
        self.apply_qft(qc, self.num_qubits)
        qc.measure_all()
        self.circuit = qc

    def run(self):
        self.build_circuit()
        compiled = transpile(self.circuit, self.backend)
        job = self.backend.run(compiled, shots=self.shots)
        result = job.result()
        self.counts = result.get_counts()
        self.display_results()

    def display_results(self):
        print("Measurement Results (QFT Periodic Input):")
        print(self.counts)


if __name__ == "__main__":
    program = QFTProgram()
    program.run()
