from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer


class GroverSearchWithDiffusionAssertion:
    def __init__(self, shots=1024):
        self.n = 3
        self.shots = shots
        self.backend = Aer.get_backend("qasm_simulator")

    def build_circuit(self):
        qc = QuantumCircuit(self.n, self.n)

        # Step 1: Superposition
        qc.h(range(self.n))
        qc.barrier()

        # Step 2: Oracle (mark |101> and |110>)
        qc.cz(2, 0)
        qc.cz(2, 1)
        qc.barrier()

        # Step 3: Diffusion operator
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
        counts = result.get_counts()

        # ----- GOLD ASSERTION START -----
        target_states = ["101", "110"]
        total_target = sum(counts.get(s, 0) for s in target_states)
        max_non_target = max(
            [cnt for state, cnt in counts.items() if state not in target_states],
            default=0,
        )

        assert total_target > max_non_target, (
            f"Expected targets {target_states} to dominate, "
            f"but got counts={counts}"
        )
        # ----- GOLD ASSERTION END -----

        return counts


if __name__ == "__main__":
    grover = GroverSearchWithDiffusionAssertion()
    output = grover.run()
    print("Diffusion operator assertion passed.")
    print("Measurement Counts:", output)
