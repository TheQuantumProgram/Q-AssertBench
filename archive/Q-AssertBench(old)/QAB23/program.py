from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer


class GroverSearch:
    def __init__(self, shots=1024):
        self.n = 3
        self.shots = shots
        self.backend = Aer.get_backend("qasm_simulator")

    def build_circuit(self):
        qc = QuantumCircuit(self.n, self.n)

        # Step 1: superposition
        qc.h(range(self.n))
        qc.barrier()

        # Step 2: Oracle (mark |101> and |110>)
        qc.cz(2, 0)
        qc.cz(2, 1)
        qc.barrier()

        # Step 3: Diffusion operator (inversion about mean)
        qc.h(range(self.n))
        qc.x(range(self.n))
        qc.barrier()
        qc.h(2)
        qc.ccx(0, 1, 2)
        qc.h(2)
        qc.barrier()
        qc.x(range(self.n))
        qc.h(range(self.n))

        # Step 4: Measurement
        qc.measure(range(self.n), range(self.n))
        return qc

    def run(self):
        qc = self.build_circuit()
        transpiled = transpile(qc, self.backend)
        job = self.backend.run(transpiled, shots=self.shots)
        result = job.result()
        return result.get_counts()


if __name__ == "__main__":
    grover = GroverSearch()
    output = grover.run()
    print("Grover search results (3 qubits):", output)
