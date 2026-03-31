"""Benchmark task loading helpers."""

from __future__ import annotations

from dataclasses import dataclass, replace
import importlib.util
from pathlib import Path
from typing import Any
from uuid import uuid4

import yaml

from qasserbench.benchmark.schema import BenchmarkTask
from qasserbench.execution.interfaces import GoldAssertionResult, ProgramDefinition


def load_task_manifest(manifest_path: str | Path) -> BenchmarkTask:
    """Load and validate a benchmark task manifest."""

    manifest_file = Path(manifest_path).resolve()
    with manifest_file.open("r", encoding="utf-8") as handle:
        manifest_data: Any = yaml.safe_load(handle) or {}

    if not isinstance(manifest_data, dict):
        raise ValueError("Task manifest root must be a mapping.")

    return BenchmarkTask.from_manifest(manifest_data, manifest_file)


@dataclass(frozen=True)
class LoadedTaskAssets:
    """Loaded assets for one benchmark task."""

    task: BenchmarkTask
    prompt_text: str
    program: ProgramDefinition
    gold_evaluator: Any
    gold_source: str
    fault_programs: dict[str, ProgramDefinition]


def _load_python_object(task_dir: Path, entry_spec: str) -> Any:
    relative_path, object_name = entry_spec.split(":", 1)
    module_path = (task_dir / relative_path).resolve()
    module_name = f"qasserbench_task_{task_dir.name}_{module_path.stem}_{uuid4().hex}"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {module_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, object_name)


def _coerce_program_definition(entry_object: Any, gold_evaluator: Any) -> ProgramDefinition:
    if isinstance(entry_object, ProgramDefinition):
        program = entry_object
    elif callable(entry_object):
        candidate = entry_object()
        if not isinstance(candidate, ProgramDefinition):
            raise TypeError("Program entry callable must return ProgramDefinition.")
        program = candidate
    else:
        raise TypeError("Program entry must resolve to ProgramDefinition or a factory.")

    return replace(program, evaluate_gold_assertion=gold_evaluator)


def _placeholder_gold_evaluator(_: Any) -> GoldAssertionResult:
    return GoldAssertionResult(
        passed=False,
        details={"note": "Gold evaluator was not loaded."},
    )


def load_task_assets(manifest_path: str | Path) -> LoadedTaskAssets:
    """Load prompt, program, gold assets, and fault variants for one task."""

    task = load_task_manifest(manifest_path)
    prompt_text = task.prompt_path.read_text(encoding="utf-8")

    gold_evaluator = _load_python_object(task.task_dir, task.gold_entry)
    if not callable(gold_evaluator):
        gold_evaluator = _placeholder_gold_evaluator

    gold_file, _ = task.gold_entry.split(":", 1)
    try:
        gold_source = _load_python_object(task.task_dir, f"{gold_file}:GOLD_SOURCE")
    except AttributeError:
        gold_source = ""

    program_entry_object = _load_python_object(task.task_dir, task.program_entry)
    program = _coerce_program_definition(program_entry_object, gold_evaluator)

    fault_programs: dict[str, ProgramDefinition] = {}
    for variant in task.fault_variants:
        fault_id = str(variant["id"])
        path = str(variant["path"])
        entry = str(variant.get("entry", "PROGRAM"))
        fault_object = _load_python_object(task.task_dir, f"{path}:{entry}")
        fault_programs[fault_id] = _coerce_program_definition(fault_object, gold_evaluator)

    return LoadedTaskAssets(
        task=task,
        prompt_text=prompt_text,
        program=program,
        gold_evaluator=gold_evaluator,
        gold_source=str(gold_source),
        fault_programs=fault_programs,
    )
