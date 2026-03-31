"""Injection helpers for candidate assertion artifacts."""

from __future__ import annotations

from qasserbench.generation.artifacts import CandidateAssertionArtifact


DEFAULT_ASSERTION_MARKER = "# ASSERTION_HOOK"


def inject_candidate_artifact(
    base_source: str,
    artifact: CandidateAssertionArtifact,
    insertion_mode: str,
    marker: str = DEFAULT_ASSERTION_MARKER,
) -> str:
    """Inject a candidate artifact into a program template."""

    if not artifact.is_usable:
        raise ValueError("Cannot inject an unusable candidate artifact.")

    if insertion_mode == "full_program_replace":
        return artifact.code or ""

    if insertion_mode != "assertion_block":
        raise ValueError(f"Unsupported insertion mode: {insertion_mode}")

    lines = base_source.splitlines()
    for index, line in enumerate(lines):
        if marker not in line:
            continue

        indent = line[: len(line) - len(line.lstrip(" "))]
        injected_lines = [f"{indent}{candidate_line}" if candidate_line else "" for candidate_line in artifact.code.splitlines()]
        replacement = "\n".join(injected_lines)
        return base_source.replace(line, replacement, 1)

    raise ValueError(f"Injection marker not found: {marker}")
