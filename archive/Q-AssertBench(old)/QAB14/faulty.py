from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

class DeutschJozsaCircuit:
    def __init__(self, oracle_type=0, shots=1024):
        """
        Faulty version: Oracle always implemented as balanced, even if oracle_type=0
        """
        self.oracle_type = oracle_type
        self.shots = shots
        self.circuit = QuantumCircuit(3, 2)
        self.backend = Aer.get_backend("qasm_simulator")

    def apply_oracle(self):
        # ❌ Faulty: always balanced
        self.circuit.cx(0, 2)
        self.circuit.cx(1, 2)

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
        return counts

if __name__ == "__main__":
    for oracle_type in [0, 1]:
        circuit_runner = DeutschJozsaCircuit(oracle_type=oracle_type)
        output = circuit_runner.run()
        print(f"Faulty Oracle type {oracle_type}, Measurement Counts:", output)
