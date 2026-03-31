from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer


class GroverSearch:
    def __init__(self, shots=1024):
        self.n = 3
        self.shots = shots
        self.backend = Aer.get_backend("qasm_simulator")

    def build_circuit(self):
        qc = QuantumCircuit(self.n, self.n)

        qc.h(range(self.n))
        qc.barrier()

        qc.cz(2, 0)
        qc.cz(2, 1)
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
        counts = result.get_counts()

        # ----- GOLD ASSERTION START -----
        # Expect results dominated by |101> and |110>
        target_states = ["101", "110"]
        total_target = sum(counts.get(s, 0) for s in target_states)
        ratio = total_target / self.shots
        assert ratio > 0.8, f"Expected target states to dominate, got {counts}"
        # ----- GOLD ASSERTION END -----

        return counts


if __name__ == "__main__":
    grover = GroverSearch()
    output = grover.run()
    print("Grover search with assertion passed.")
    print("Results:", output)
