from __future__ import annotations

from qasserbench.execution.interfaces import ExecutionResult, GoldAssertionResult


MIN_UNIQUE_INPUTS = 6

GOLD_SOURCE = """
register_width = result.metadata.get("register_width", 3)
xor_mask = result.metadata.get("xor_mask", "101")
relation_violations = []
unique_inputs = set()

for bitstring in counts:
    output_bits = bitstring[:-register_width]
    input_bits = bitstring[-register_width:]
    unique_inputs.add(input_bits)
    observed_mask = "".join(
        str(int(output_bit) ^ int(input_bit))
        for output_bit, input_bit in zip(output_bits, input_bits)
    )
    if observed_mask != xor_mask:
        relation_violations.append((input_bits, output_bits, observed_mask))

assert not relation_violations, f"Observed register pairs that violate the XOR relation: {relation_violations}"
assert len(unique_inputs) >= 6, f"Expected broad input support, but got {sorted(unique_inputs)}"
""".strip()


def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
    register_width = int(result.metadata.get("register_width", 3))
    xor_mask = str(result.metadata.get("xor_mask", "101"))
    relation_violations: list[tuple[str, str, str]] = []
    unique_inputs: set[str] = set()

    for bitstring in result.counts:
        output_bits = bitstring[:-register_width]
        input_bits = bitstring[-register_width:]
        unique_inputs.add(input_bits)
        observed_mask = "".join(
            str(int(output_bit) ^ int(input_bit))
            for output_bit, input_bit in zip(output_bits, input_bits)
        )
        if observed_mask != xor_mask:
            relation_violations.append((input_bits, output_bits, observed_mask))

    try:
        assert not relation_violations
        assert len(unique_inputs) >= MIN_UNIQUE_INPUTS
    except AssertionError as exc:
        return GoldAssertionResult(
            passed=False,
            details={
                "message": str(exc),
                "register_width": register_width,
                "xor_mask": xor_mask,
                "relation_violations": relation_violations,
                "unique_inputs": sorted(unique_inputs),
                "counts": dict(result.counts),
            },
        )

    return GoldAssertionResult(
        passed=True,
        details={
            "register_width": register_width,
            "xor_mask": xor_mask,
            "relation_violations": relation_violations,
            "unique_inputs": sorted(unique_inputs),
            "counts": dict(result.counts),
        },
    )
