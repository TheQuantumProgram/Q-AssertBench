from qiskit import QuantumCircuit
from qiskit_aer import Aer
from math import pi

class SuperpositionCircuit:
    def __init__(self):
        self.qc = QuantumCircuit(5, 5)
        self._build()
        
    def _build(self):
        # Qubit 0: Superposition
        self.qc.h(0)

        # Qubits 1, 2: Classical 1 and 0
        self.qc.x(1)
        # Qubit 2 remains in |0⟩

        # Qubit 3: U3 for ~1/3 probability of |1⟩
        self.qc.u(2 * pi / 3, 0, 0, 3)

        # Qubit 4: U3 for ~2/3 probability of |1⟩
        self.qc.u(2 * pi / 9, 0, 0, 4)

        self.qc.measure(range(5), range(5))
    
    def run(self):
        backend = Aer.get_backend('qasm_simulator')
        job = backend.run(self.qc, shots=1024)
        return job.result().get_counts()

if __name__ == "__main__":
    circuit = SuperpositionCircuit()
    counts = circuit.run()
    print(counts)

