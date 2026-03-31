from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

class InterferenceControlCircuit:
    def __init__(self, shots=1024):
        self.shots = shots
        self.circuit = QuantumCircuit(3, 3)
        self.backend = Aer.get_backend("qasm_simulator")

    def build_circuit(self):
        # Step 1: Create superposition on q0
        self.circuit.h(0)

        # Step 2: Controlled propagation
        self.circuit.cx(0, 1)  # q0 controls q1
        self.circuit.cx(1, 2)  # q1 controls q2

        # Step 3: Measurement
        self.circuit.measure(range(3), range(3))

    def run(self):
        self.build_circuit()
        transpiled = transpile(self.circuit, self.backend)
        job = self.backend.run(transpiled, shots=self.shots)
        result = job.result()
        counts = result.get_counts()
        return counts

if __name__ == "__main__":
    circuit_runner = InterferenceControlCircuit()
    output = circuit_runner.run()
    print("Measurement Counts:", output)
