"""Runtime helpers shared across benchmark tasks."""

from __future__ import annotations

from collections.abc import Mapping


def normalize_counts(raw_counts: Mapping[str, int]) -> dict[str, int]:
    """Return a deterministic counts dictionary sorted by bitstring key."""

    normalized = {str(bitstring): int(count) for bitstring, count in raw_counts.items()}
    return dict(sorted(normalized.items(), key=lambda item: item[0]))
