from program import QFTProgram


class QFTAssertion:
    """
    Golden Assertion for QAB-29 with 10-qubit QFT on periodic input.
    Check if measurement is concentrated on expected frequency states ±1.
    """

    def __init__(self, threshold=0.5):
        self.threshold = threshold
        self.program = QFTProgram(plot=False)
        self.n = self.program.num_qubits
        self.expected_freq_step = 2 ** self.n // self.program.period

    def assert_frequency_peaks(self):
        self.program.run()
        counts = self.program.counts
        total = sum(counts.values())

        # Build list of expected states (±1 offset included)
        expected_states = []
        for k in range(self.program.period):
            center = k * self.expected_freq_step
            for delta in [-1, 0, 1]:  # allow near misses
                idx = center + delta
                if 0 <= idx < 2 ** self.n:
                    expected_states.append(format(idx, f'0{self.n}b'))

        hit = sum(counts.get(state, 0) for state in expected_states)
        ratio = hit / total

        print(f"[GOLD ASSERTION] Expected peak states (±1): {expected_states}")
        print(f"[GOLD ASSERTION] Hit ratio: {ratio:.3f}")

        assert ratio > self.threshold, f"Expected QFT peak structure missing: ratio={ratio:.3f}"

    def run_all(self):
        self.assert_frequency_peaks()
        print("[✅] QAB-29 assertion passed.")


if __name__ == "__main__":
    test = QFTAssertion()
    test.run_all()
