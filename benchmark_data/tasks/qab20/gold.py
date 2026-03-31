from __future__ import annotations

from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


HIDDEN_PERIOD = "11"

GOLD_SOURCE = """
mapping = {}
for bitstring in counts:
    outputs = bitstring[:2]
    inputs = bitstring[-2:]
    mapping[inputs] = outputs

def xor_bitstrings(left, right):
    return "".join(str(int(left_bit) ^ int(right_bit)) for left_bit, right_bit in zip(left, right))

hidden_period = "11"
for inputs, outputs in mapping.items():
    paired_inputs = xor_bitstrings(inputs, hidden_period)
    assert paired_inputs in mapping, f"Missing paired input for {inputs}"
    assert mapping[paired_inputs] == outputs, (
        f"Periodicity broken: f({inputs})={outputs}, f({paired_inputs})={mapping[paired_inputs]}"
    )
""".strip()


def _xor_bitstrings(left: str, right: str) -> str:
    return "".join(str(int(left_bit) ^ int(right_bit)) for left_bit, right_bit in zip(left, right))


def _build_mapping(counts: dict[str, int]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for bitstring in counts:
        outputs = bitstring[:2]
        inputs = bitstring[-2:]
        mapping[inputs] = outputs
    return mapping


def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
    mapping = _build_mapping(result.counts)

    try:
        for inputs, outputs in mapping.items():
            paired_inputs = _xor_bitstrings(inputs, HIDDEN_PERIOD)
            assert paired_inputs in mapping
            assert mapping[paired_inputs] == outputs
    except AssertionError as exc:
        return GoldAssertionResult(
            passed=False,
            details={"message": str(exc), "mapping": mapping, "counts": dict(result.counts)},
        )

    return GoldAssertionResult(
        passed=True,
        details={"mapping": mapping, "counts": dict(result.counts)},
    )
