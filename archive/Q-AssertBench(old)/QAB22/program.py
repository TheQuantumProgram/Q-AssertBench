import math
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer


class QuantumFourierTransformWithInverse:
    def __init__(self, n=3, shots=1024):
        """
        QFT followed by QFT† should return the original state.
        n: number of qubits
        shots: number of measurements
        """
        self.n = n
        self.shots = shots
        self.backend = Aer.get_backend("qasm_simulator")

    def apply_qft(self, circuit):
        """Apply QFT."""
        for j in range(self.n):
            circuit.h(j)
            for k in range(j + 1, self.n):
                angle = math.pi / float(2 ** (k - j))
                circuit.cp(angle, k, j)
        circuit.barrier()

    def apply_qft_dagger(self, circuit):
        """Apply QFT† (inverse QFT)."""
        for j in range(self.n):
            k = (self.n - 1) - j
            for m in range(k):
                angle = -math.pi / float(2 ** (k - m))
                circuit.cp(angle, k, m)
            circuit.h(k)
        circuit.barrier()

    def build_and_run(self, prepare_input=None):
        circuit = QuantumCircuit(self.n, self.n)

        # Prepare input state
        if prepare_input:
            prepare_input(circuit)

        # Apply QFT then QFT†
        self.apply_qft(circuit)
        self.apply_qft_dagger(circuit)

        # Measure
        circuit.measure(range(self.n), range(self.n))

        transpiled = transpile(circuit, self.backend)
        job = self.backend.run(transpiled, shots=self.shots)
        result = job.result()
        return result.get_counts()


if __name__ == "__main__":
    qft_runner = QuantumFourierTransformWithInverse(n=3, shots=1024)

    # Example: input state |101>
    def prepare_input(circuit):
        circuit.x(0)
        circuit.x(2)

    counts = qft_runner.build_and_run(prepare_input=prepare_input)

    print("QFT followed by QFT† Result on input |101> (3 qubits):")
    for bitstring, cnt in counts.items():
        print(f"{bitstring}: {cnt}")
