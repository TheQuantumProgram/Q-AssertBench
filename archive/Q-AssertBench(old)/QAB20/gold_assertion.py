from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

def build_oracle_circuit(shots=1024):
    """
    Periodic oracle example with hidden period a = "11".
    Function: f(x0, x1) = (x0 XOR x1, x0 XOR x1).
    Inputs: qubits 0,1
    Outputs: qubits 2,3
    """
    qc = QuantumCircuit(4, 4)

    # Prepare uniform superposition over inputs
    qc.h(0)
    qc.h(1)

    # Oracle construction
    qc.cx(0, 2)
    qc.cx(1, 2)
    qc.cx(0, 3)
    qc.cx(1, 3)

    # Measure all qubits
    qc.measure([0, 1, 2, 3], [0, 1, 2, 3])
    return qc

def run_oracle(shots=1024):
    backend = Aer.get_backend("qasm_simulator")
    qc = build_oracle_circuit(shots)
    transpiled = transpile(qc, backend)
    job = backend.run(transpiled, shots=shots)
    result = job.result()
    return result.get_counts()

if __name__ == "__main__":
    a = "11"  # hidden period
    counts = run_oracle()

    # Build mapping input->output
    mapping = {}
    for bitstring, cnt in counts.items():
        outputs = bitstring[:2]   # q3q2
        inputs  = bitstring[-2:]  # q1q0
        mapping[inputs] = outputs

    # ----- GOLD ASSERTION START -----
    def xor_strings(s1, s2):
        return "".join(str(int(b1) ^ int(b2)) for b1, b2 in zip(s1, s2))

    for x, fx in mapping.items():
        x_pair = xor_strings(x, a)
        if x_pair in mapping:
            assert mapping[x_pair] == fx, (
                f"Periodicity broken: f({x})={fx}, f({x_pair})={mapping[x_pair]}"
            )
    # ----- GOLD ASSERTION END -----

    print("Oracle mapping verified with period", a)
    for x, fx in mapping.items():
        print(f"Input {x} -> Output {fx}")
