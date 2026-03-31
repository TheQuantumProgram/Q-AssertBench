from qiskit import QuantumCircuit
from qiskit_aer import Aer

class NonEntangledCircuit:
    def __init__(self):
        self.qc = QuantumCircuit(2, 2)

    def build(self):
        self.qc.h(0)
        self.qc.h(1)  # Fault: both qubits in superposition, but not entangled
        self.qc.measure([0, 1], [0, 1])
        return self.qc

if __name__ == "__main__":
    circuit = NonEntangledCircuit().build()
    backend = Aer.get_backend('qasm_simulator')
    job = backend.run(circuit, shots=1024)
    result = job.result()
    counts = result.get_counts()
    print(counts)
