from __future__ import annotations

from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


EXPECTED_OUTCOMES = {format(index, "03b") for index in range(8)}
MAX_SPREAD = 0.05

GOLD_SOURCE = """
expected_outcomes = {format(index, "03b") for index in range(8)}
observed_outcomes = set(counts)
probabilities = {bitstring: counts.get(bitstring, 0) / shots for bitstring in expected_outcomes}

assert observed_outcomes == expected_outcomes, (
    f"Expected all eight outcomes, got {sorted(observed_outcomes)}"
)
assert max(probabilities.values()) - min(probabilities.values()) < 0.05, (
    "Outcome probabilities are not uniform enough"
)
""".strip()


def _measure_probabilities(counts: dict[str, int], shots: int) -> dict[str, float]:
    return {
        bitstring: counts.get(bitstring, 0) / shots
        for bitstring in sorted(EXPECTED_OUTCOMES)
    }


def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
    observed_outcomes = set(result.counts)
    probabilities = _measure_probabilities(result.counts, result.shots)
    spread = max(probabilities.values()) - min(probabilities.values())

    try:
        assert observed_outcomes == EXPECTED_OUTCOMES
        assert spread < MAX_SPREAD
    except AssertionError as exc:
        return GoldAssertionResult(
            passed=False,
            details={
                "message": str(exc),
                "observed_outcomes": sorted(observed_outcomes),
                "expected_outcomes": sorted(EXPECTED_OUTCOMES),
                "probabilities": probabilities,
                "spread": spread,
                "max_spread": MAX_SPREAD,
            },
        )

    return GoldAssertionResult(
        passed=True,
        details={
            "observed_outcomes": sorted(observed_outcomes),
            "expected_outcomes": sorted(EXPECTED_OUTCOMES),
            "probabilities": probabilities,
            "spread": spread,
            "max_spread": MAX_SPREAD,
        },
    )
