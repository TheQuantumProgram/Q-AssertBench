"""Extraction helpers for model-generated assertion candidates."""

from __future__ import annotations

import re

from qasserbench.generation.artifacts import CandidateAssertionArtifact


CODE_BLOCK_PATTERN = re.compile(r"```(?:python)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def extract_candidate_assertion(
    raw_response: str,
    extraction_mode: str,
) -> CandidateAssertionArtifact:
    """Extract candidate code from a raw model response."""

    response = raw_response.strip()
    if not response:
        return CandidateAssertionArtifact(
            raw_response=raw_response,
            code=None,
            extraction_mode=extraction_mode,
            diagnostics=("empty_response",),
        )

    match = CODE_BLOCK_PATTERN.search(response)
    code = match.group(1).strip() if match else response

    diagnostics: tuple[str, ...] = ()
    if not match and response.startswith("```"):
        diagnostics = ("unparsed_code_fence",)

    return CandidateAssertionArtifact(
        raw_response=raw_response,
        code=code,
        extraction_mode=extraction_mode,
        diagnostics=diagnostics,
    )
