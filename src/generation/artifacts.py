"""Candidate assertion artifacts extracted from model responses."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CandidateAssertionArtifact:
    """Normalized candidate assertion payload."""

    raw_response: str
    code: str | None
    extraction_mode: str
    diagnostics: tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_usable(self) -> bool:
        return bool(self.code and self.code.strip())
