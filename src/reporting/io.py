"""Persistence helpers for trial-level experiment records."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_trial_results(records: list[dict[str, Any]], output_path: str | Path) -> Path:
    """Write trial-level records as JSONL."""

    destination = Path(output_path).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)

    with destination.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    return destination


def read_trial_results(input_path: str | Path) -> list[dict[str, Any]]:
    """Read trial-level JSONL records."""

    source = Path(input_path).resolve()
    records: list[dict[str, Any]] = []
    with source.open("r", encoding="utf-8") as handle:
        for line in handle:
            payload = line.strip()
            if not payload:
                continue
            records.append(json.loads(payload))
    return records


def write_summary(summary: dict[str, Any], output_path: str | Path) -> Path:
    """Write an aggregate summary as pretty JSON."""

    destination = Path(output_path).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return destination
