"""Structured benchmark task definitions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_TASK_FIELDS = (
    "task_id",
    "title",
    "family",
    "property_type",
    "qubit_count",
    "shots",
    "llm_source_line_count",
    "circuit_gate_count",
    "program_entry",
    "gold_entry",
    "gold_compare_mode",
    "gold_metadata",
    "fault_variants",
    "insertion_mode",
    "prompt_file",
)


@dataclass(frozen=True)
class BenchmarkTask:
    """Normalized benchmark task manifest."""

    task_id: str
    title: str
    family: str
    property_type: str
    qubit_count: int
    shots: int
    llm_source_line_count: int
    circuit_gate_count: int
    program_entry: str
    gold_entry: str
    gold_compare_mode: str
    gold_metadata: dict[str, Any]
    fault_variants: list[dict[str, Any]]
    insertion_mode: str
    prompt_file: str
    task_dir: Path
    manifest_path: Path
    prompt_path: Path

    @classmethod
    def from_manifest(cls, manifest: dict[str, Any], manifest_path: Path) -> "BenchmarkTask":
        missing_fields = [field for field in REQUIRED_TASK_FIELDS if field not in manifest]
        if missing_fields:
            missing = ", ".join(missing_fields)
            raise ValueError(f"Task manifest is missing required fields: {missing}")

        task_dir = manifest_path.parent.resolve()
        prompt_file = str(manifest["prompt_file"])
        prompt_path = (task_dir / prompt_file).resolve()

        gold_metadata = manifest["gold_metadata"]
        fault_variants = manifest["fault_variants"]

        if not isinstance(gold_metadata, dict):
            raise ValueError("Task manifest field 'gold_metadata' must be a mapping.")
        if not isinstance(fault_variants, list):
            raise ValueError("Task manifest field 'fault_variants' must be a list.")

        normalized_fault_variants: list[dict[str, Any]] = []
        for index, variant in enumerate(fault_variants):
            if not isinstance(variant, dict):
                raise ValueError(
                    f"Task manifest fault variant at index {index} must be a mapping."
                )
            normalized_fault_variants.append(dict(variant))

        return cls(
            task_id=str(manifest["task_id"]),
            title=str(manifest["title"]),
            family=str(manifest["family"]),
            property_type=str(manifest["property_type"]),
            qubit_count=int(manifest["qubit_count"]),
            shots=int(manifest["shots"]),
            llm_source_line_count=int(manifest["llm_source_line_count"]),
            circuit_gate_count=int(manifest["circuit_gate_count"]),
            program_entry=str(manifest["program_entry"]),
            gold_entry=str(manifest["gold_entry"]),
            gold_compare_mode=str(manifest["gold_compare_mode"]),
            gold_metadata=dict(gold_metadata),
            fault_variants=normalized_fault_variants,
            insertion_mode=str(manifest["insertion_mode"]),
            prompt_file=prompt_file,
            task_dir=task_dir,
            manifest_path=manifest_path.resolve(),
            prompt_path=prompt_path,
        )
