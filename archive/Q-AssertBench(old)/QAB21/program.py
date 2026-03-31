import math
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer


class QuantumFourierTransform:
    def __init__(self, n=3, shots=1024):
        """
        Quantum Fourier Transform (QFT) implementation.
        n: number of qubits
        shots: number of measurements
        """
        self.n = n
        self.shots = shots
        self.backend = Aer.get_backend("qasm_simulator")

    def apply_qft(self, circuit):
        """Apply QFT on the first n qubits."""
        for j in range(self.n):
            circuit.h(j)
            for k in range(j + 1, self.n):
                angle = math.pi / float(2 ** (k - j))
                circuit.cp(angle, k, j)  # controlled-phase rotation
        circuit.barrier()

    def build_and_run(self, prepare_input=None):
        """
        Build a circuit, optionally apply a custom state preparation, 
        then apply QFT and run the simulation.
        """
        circuit = QuantumCircuit(self.n, self.n)

        # Prepare input state
        if prepare_input:
            prepare_input(circuit)

        # Apply QFT
        self.apply_qft(circuit)

        # Measure all qubits
        circuit.measure(range(self.n), range(self.n))

        transpiled = transpile(circuit, self.backend)
        job = self.backend.run(transpiled, shots=self.shots)
        result = job.result()
        return result.get_counts()


if __name__ == "__main__":
    qft_runner = QuantumFourierTransform(n=3, shots=1024)

    # Example: prepare a periodic input state
    # State = (|0> + |4>)/√2  in the computational basis
    def prepare_periodic(circuit):
        circuit.h(0)      # put q0 in superposition
        circuit.x(2)      # shift q2 to create |100> component

    output = qft_runner.build_and_run(prepare_input=prepare_periodic)

    print("QFT Result on periodic input state (3 qubits):")
    for bitstring, cnt in output.items():
        print(f"{bitstring}: {cnt}")
