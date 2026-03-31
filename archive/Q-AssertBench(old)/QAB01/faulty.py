from qiskit import QuantumCircuit
from qiskit_aer import Aer
from math import pi

class FaultySuperpositionCircuit:
    def __init__(self):
        self.qc = QuantumCircuit(5, 5)
        self._build()
        
    def _build(self):
        # Replace q1, q2 with H gates — no classical states
        self.qc.h(0)
        self.qc.h(1)
        self.qc.h(2)

        self.qc.u(2 * pi / 3, 0, 0, 3)
        self.qc.u(2 * pi / 9, 0, 0, 4)

        self.qc.measure(range(5), range(5))

    def run(self):
        backend = Aer.get_backend('qasm_simulator')
        job = backend.run(self.qc, shots=1024)
        return job.result().get_counts()

if __name__ == "__main__":
    circuit = FaultySuperpositionCircuit()
    counts = circuit.run()
    print(counts)