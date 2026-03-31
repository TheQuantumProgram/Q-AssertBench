"""Repeated generation driver for benchmark trials."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Sequence

from qasserbench.benchmark.loader import load_task_assets, load_task_manifest
from qasserbench.generation.clients import ModelClient
from qasserbench.generation.prompting import PROMPT_TEMPLATE_VERSION, render_task_prompt


def discover_task_manifests(
    tasks_root: str | Path,
    task_ids: Sequence[str] | None = None,
) -> list[Path]:
    """Discover task manifests, optionally filtered by task id."""

    root = Path(tasks_root).resolve()
    selected = {task_id.upper() for task_id in task_ids} if task_ids else None

    manifest_paths: list[Path] = []
    for manifest_path in sorted(root.glob("*/task.yaml")):
        task = load_task_manifest(manifest_path)
        if selected and task.task_id.upper() not in selected:
            continue
        manifest_paths.append(manifest_path.resolve())

    return manifest_paths


def write_generation_records(records: Iterable[dict[str, Any]], output_path: str | Path) -> Path:
    """Persist raw generation records as JSONL."""

    destination = Path(output_path).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)

    with destination.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    return destination


def read_generation_records(input_path: str | Path) -> list[dict[str, Any]]:
    """Load raw generation records from a JSONL file."""

    source = Path(input_path).resolve()
    records: list[dict[str, Any]] = []
    with source.open("r", encoding="utf-8") as handle:
        for line in handle:
            payload = line.strip()
            if not payload:
                continue
            records.append(json.loads(payload))
    return records


def _standardized_generation_metadata(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "generation_temperature": payload.get("temperature"),
        "generation_max_output_tokens": payload.get("max_output_tokens"),
        "prompt_tokens": payload.get("prompt_tokens"),
        "completion_tokens": payload.get("completion_tokens"),
        "total_tokens": payload.get("total_tokens"),
    }


def run_generation_trials(
    *,
    manifest_paths: Sequence[str | Path],
    client: ModelClient,
    trial_count: int,
    output_path: str | Path,
) -> Path:
    """Run repeated generation trials and persist the raw responses."""

    if trial_count < 1:
        raise ValueError("trial_count must be at least 1.")

    records: list[dict[str, Any]] = []
    for manifest_path in manifest_paths:
        assets = load_task_assets(manifest_path)
        task = assets.task
        rendered_prompt = render_task_prompt(assets)

        for trial_index in range(1, trial_count + 1):
            response = client.generate(
                prompt_text=rendered_prompt,
                task_id=task.task_id,
                trial_index=trial_index,
            )
            standardized_metadata = _standardized_generation_metadata(dict(response.payload))
            records.append(
                {
                    "model_id": client.model_id,
                    "task_id": task.task_id,
                    "trial_index": trial_index,
                    "task_family": task.family,
                    "property_type": task.property_type,
                    "manifest_path": str(Path(manifest_path).resolve()),
                    "prompt_version": PROMPT_TEMPLATE_VERSION,
                    "raw_response": response.text,
                    "raw_payload": dict(response.payload),
                    **standardized_metadata,
                }
            )

    return write_generation_records(records, output_path)
