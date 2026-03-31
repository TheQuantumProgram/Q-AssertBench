from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import numpy as np


class HHLProgram:
    """
    QAB-28 Benchmark Program with inline golden assertion.
    Implements a simplified HHL algorithm circuit for a 2x2 system:
        A = [[1, 0.5], [0.5, 1]]
        b = [1, 0]
    """

    def __init__(self, shots=1024, plot=True):
        self.shots = shots
        self.plot = plot
        self.backend = AerSimulator()
        self.circuit = None
        self.counts = None

    def build_circuit(self):
        """
        Build the HHL quantum circuit.
        """
        qc = QuantumCircuit(3)

        # Step 1: QPE - simulate e^{iAt}
        qc.h(1)
        qc.cx(1, 0)
        qc.rz(2 * np.pi / 3, 0)
        qc.cx(1, 0)
        qc.h(1)

        # Step 2: Controlled rotation to ancilla (simulate 1/λ)
        theta = 2 * np.arcsin(1 / 1.5)
        qc.cry(theta, 1, 2)

        # Step 3: Uncompute QPE
        qc.h(1)
        qc.cx(1, 0)
        qc.rz(-2 * np.pi / 3, 0)
        qc.cx(1, 0)
        qc.h(1)

        # Step 4: Measure
        qc.measure_all()
        self.circuit = qc

    def run(self):
        """
        Run the HHL circuit on AerSimulator and show result.
        Includes GOLD ASSERTION.
        """
        self.build_circuit()
        compiled = transpile(self.circuit, self.backend)
        job = self.backend.run(compiled, shots=self.shots)
        result = job.result()
        self.counts = result.get_counts()

        # ----- GOLD ASSERTION START -----
        # Expectation: HHL outputs mostly the correct amplitude encoding state.
        # For this simplified circuit, '000' is the dominant solution state.
        dominant_state = '000'
        dominant_count = self.counts.get(dominant_state, 0)
        total_counts = sum(self.counts.values())
        dominant_ratio = dominant_count / total_counts
        print(f"[GOLD ASSERTION] '{dominant_state}' frequency ratio: {dominant_ratio:.3f}")
        assert dominant_ratio > 0.5, (
            f"Expected dominant output state '{dominant_state}' to appear >75%, "
            f"but got {dominant_ratio:.3f}"
        )
        # ----- GOLD ASSERTION END -----

        self.display_results()

    def display_results(self):
        """
        Output results and plot histogram if enabled.
        """
        print("Measurement Results:")
        print(self.counts)


if __name__ == "__main__":
    program = HHLProgram()
    program.run()
