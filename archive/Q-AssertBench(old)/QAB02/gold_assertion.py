from qiskit import QuantumCircuit
from qiskit_aer import Aer

class BellStateCircuit:
    def __init__(self):
        self.qc = QuantumCircuit(2, 2)

    def build(self):
        self.qc.h(0)
        self.qc.cx(0, 1)
        self.qc.measure([0, 1], [0, 1])
        return self.qc

if __name__ == "__main__":
    circuit = BellStateCircuit().build()
    backend = Aer.get_backend('qasm_simulator')
    job = backend.run(circuit, shots=1024)
    result = job.result()
    counts = result.get_counts()
    #print(counts)
    
    # === GOLD ASSERTION ===
    shots = 1024
    ratio_00 = counts.get('00', 0) / shots
    ratio_11 = counts.get('11', 0) / shots
    assert all(k in ['00', '11'] for k in counts), "Unexpected outcomes detected"
    assert 0.4 <= ratio_00 <= 0.6 and 0.4 <= ratio_11 <= 0.6, "Imbalanced distribution — likely not Bell state"
    # ======================

