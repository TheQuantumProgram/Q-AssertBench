from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

class DeutschJozsaCircuit:
    def __init__(self, oracle_type=0, shots=1024):
        """
        oracle_type = 0 → constant function f(x)=0
        oracle_type = 1 → balanced function f(x0, x1) = x0 XOR x1
        """
        self.oracle_type = oracle_type
        self.shots = shots
        self.circuit = QuantumCircuit(3, 2)
        self.backend = Aer.get_backend("qasm_simulator")

    def apply_oracle(self):
        if self.oracle_type == 0:
            pass
        elif self.oracle_type == 1:
            self.circuit.cx(0, 2)
            self.circuit.cx(1, 2)
        else:
            raise ValueError("oracle_type must be 0 or 1")

    def build_circuit(self):
        self.circuit.x(2)
        for i in range(3):
            self.circuit.h(i)
        self.apply_oracle()
        self.circuit.h(0)
        self.circuit.h(1)
        self.circuit.measure(0, 0)
        self.circuit.measure(1, 1)

    def run(self):
        self.build_circuit()
        transpiled = transpile(self.circuit, self.backend)
        job = self.backend.run(transpiled, shots=self.shots)
        result = job.result()
        counts = result.get_counts()

        # ----- GOLD ASSERTION START -----
        if self.oracle_type == 0:
            # Constant oracle → Expect nearly all results '00'
            assert "00" in counts and counts["00"] > 0.9 * self.shots, (
                f"Expected constant outcome '00', got {counts}"
            )
        elif self.oracle_type == 1:
            # Balanced oracle → Input qubits should not be all zero
            zero_counts = counts.get("00", 0)
            assert zero_counts < 0.1 * self.shots, (
                f"Expected balanced outcome (non-zero states), got {counts}"
            )
        # ----- GOLD ASSERTION END -----

        return counts

if __name__ == "__main__":
    for oracle_type in [0, 1]:
        circuit_runner = DeutschJozsaCircuit(oracle_type=oracle_type)
        output = circuit_runner.run()
        print(f"Oracle type {oracle_type}, Measurement Counts:", output)
