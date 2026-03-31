from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer


class FaultyGroverSearch:
    def __init__(self, shots=1024):
        self.n = 3
        self.shots = shots
        self.backend = Aer.get_backend("qasm_simulator")

    def build_circuit(self):
        qc = QuantumCircuit(self.n, self.n)

        qc.h(range(self.n))
        qc.barrier()

        # ❌ Faulty oracle: only marks |101>, misses |110>
        qc.cz(2, 0)
        qc.barrier()

        qc.h(range(self.n))
        qc.x(range(self.n))
        qc.barrier()
        qc.h(2)
        qc.ccx(0, 1, 2)
        qc.h(2)
        qc.barrier()
        qc.x(range(self.n))
        qc.h(range(self.n))

        qc.measure(range(self.n), range(self.n))
        return qc

    def run(self):
        qc = self.build_circuit()
        transpiled = transpile(qc, self.backend)
        job = self.backend.run(transpiled, shots=self.shots)
        result = job.result()
        return result.get_counts()


if __name__ == "__main__":
    grover = FaultyGroverSearch()
    output = grover.run()
    print("Faulty Grover results (3 qubits):", output)
