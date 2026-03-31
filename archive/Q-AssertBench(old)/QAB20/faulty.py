from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

def build_faulty_oracle_circuit(shots=1024):
    """
    Faulty periodic oracle: one CNOT gate is missing.
    Expected function: f(x0, x1) = (x0 XOR x1, x0 XOR x1),
    but this version omits one output mapping.
    """
    qc = QuantumCircuit(4, 4)

    # Prepare uniform superposition over inputs
    qc.h(0)
    qc.h(1)

    # Faulty Oracle construction (missing cx(1, 3))
    qc.cx(0, 2)
    qc.cx(1, 2)
    qc.cx(0, 3)
    # ❌ missing: qc.cx(1, 3)

    # Measure all qubits
    qc.measure([0, 1, 2, 3], [0, 1, 2, 3])
    return qc

def run_faulty_oracle(shots=1024):
    backend = Aer.get_backend("qasm_simulator")
    qc = build_faulty_oracle_circuit(shots)
    transpiled = transpile(qc, backend)
    job = backend.run(transpiled, shots=shots)
    result = job.result()
    counts = result.get_counts()
    return counts

if __name__ == "__main__":
    counts = run_faulty_oracle()
    print("Faulty Oracle Mapping Counts:")
    for bitstring, cnt in counts.items():
        # bitstring format: c3 c2 c1 c0
        outputs = bitstring[:2]   # q3q2
        inputs  = bitstring[-2:]  # q1q0
        print(f"Input {inputs} -> Output {outputs}, Count={cnt}")
