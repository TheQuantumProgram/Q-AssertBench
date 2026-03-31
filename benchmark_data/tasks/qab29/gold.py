from __future__ import annotations

from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


NUM_QUBITS = 10
PERIOD = 4
PEAK_TOLERANCE = 1
MIN_PEAK_RATIO = 0.75
MIN_REPRESENTED_PEAKS = 3
MIN_LOCAL_PEAK_RATIO = 0.03

GOLD_SOURCE = """
total = shots
peak_centers = [k * (2**10 // 4) for k in range(4)]
peak_hits = {}
represented_peaks = 0
peak_ratio = 0.0
for center in peak_centers:
    states = [format((center + delta) % (2**10), "010b") for delta in (-1, 0, 1)]
    hit = sum(counts.get(state, 0) for state in states)
    peak_hits[center] = hit
    peak_ratio += hit / total
    if hit / total >= 0.03:
        represented_peaks += 1

assert peak_ratio > 0.75, f"Expected QFT peak neighborhoods to dominate, but got ratio={peak_ratio:.3f}"
assert represented_peaks >= 3, f"Expected at least three periodic peaks, but got {represented_peaks}: {peak_hits}"
""".strip()


def _peak_centers() -> tuple[int, ...]:
    return tuple(k * (2**NUM_QUBITS // PERIOD) for k in range(PERIOD))


def _neighborhood_states(center: int) -> list[str]:
    return [
        format((center + delta) % (2**NUM_QUBITS), f"0{NUM_QUBITS}b")
        for delta in range(-PEAK_TOLERANCE, PEAK_TOLERANCE + 1)
    ]


def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
    total = result.shots
    peak_hits: dict[int, int] = {}
    represented_peaks = 0
    peak_ratio = 0.0

    for center in _peak_centers():
        hit = sum(result.counts.get(state, 0) for state in _neighborhood_states(center))
        peak_hits[center] = hit
        local_ratio = hit / total
        peak_ratio += local_ratio
        if local_ratio >= MIN_LOCAL_PEAK_RATIO:
            represented_peaks += 1

    try:
        assert peak_ratio > MIN_PEAK_RATIO
        assert represented_peaks >= MIN_REPRESENTED_PEAKS
    except AssertionError as exc:
        return GoldAssertionResult(
            passed=False,
            details={
                "message": str(exc),
                "peak_ratio": peak_ratio,
                "represented_peaks": represented_peaks,
                "peak_hits": peak_hits,
                "counts": dict(result.counts),
            },
        )

    return GoldAssertionResult(
        passed=True,
        details={
            "peak_ratio": peak_ratio,
            "represented_peaks": represented_peaks,
            "peak_hits": peak_hits,
            "counts": dict(result.counts),
        },
    )
