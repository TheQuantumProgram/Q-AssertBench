from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import numpy as np


class HHLProgram:
    """
    Faulty version of QAB-28 HHL program.
    Introduces incorrect phase rotation to simulate bug in QPE step.
    """

    def __init__(self, shots=1024, plot=True):
        self.shots = shots
        self.plot = plot
        self.backend = AerSimulator()
        self.circuit = None
        self.counts = None

    def build_circuit(self):
        """
        Build the HHL quantum circuit with incorrect QPE phase.
        """
        qc = QuantumCircuit(3)

        # Step 1: QPE - simulate e^{iAt} with WRONG phase
        qc.h(1)
        qc.cx(1, 0)

        # ❌ WRONG ROTATION: should be 2π/3, using π/3 instead
        qc.rz(np.pi, 0)

        qc.cx(1, 0)
        qc.h(1)

        # Step 2: Controlled rotation to ancilla (simulate 1/λ)
        theta = 2 * np.arcsin(1 / 1.5)
        qc.cry(theta, 1, 2)

        # Step 3: Uncompute QPE (also with wrong inverse)
        qc.h(1)
        qc.cx(1, 0)
        qc.rz(-np.pi / 3, 0)  # wrong inverse
        qc.cx(1, 0)
        qc.h(1)

        # Step 4: Measure
        qc.measure_all()
        self.circuit = qc

    def run(self):
        """
        Run the faulty HHL circuit on AerSimulator and display results.
        """
        self.build_circuit()
        compiled = transpile(self.circuit, self.backend)
        job = self.backend.run(compiled, shots=self.shots)
        result = job.result()
        self.counts = result.get_counts()

        self.display_results()

    def display_results(self):
        """
        Output results and plot histogram if enabled.
        """
        print("Measurement Results (Faulty):")
        print(self.counts)


if __name__ == "__main__":
    program = HHLProgram()
    program.run()
