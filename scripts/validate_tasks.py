"""Validate benchmark task manifests under benchmark_data/tasks."""

from __future__ import annotations

import sys
from pathlib import Path

from qasserbench.benchmark.loader import load_task_assets, load_task_manifest
from qasserbench.generation.prompting import inspect_task_prompt


def compute_task_manifest_metrics(assets) -> dict[str, int]:
    context = inspect_task_prompt(assets)
    llm_source_line_count = sum(1 for line in context.source_excerpt.splitlines() if line.strip())
    circuit = assets.program.build_program()
    count_ops = circuit.count_ops()
    circuit_gate_count = sum(
        int(count)
        for name, count in count_ops.items()
        if name not in {"measure", "barrier"}
    )
    return {
        "llm_source_line_count": llm_source_line_count,
        "circuit_gate_count": circuit_gate_count,
    }


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    tasks_root = project_root / "benchmark_data" / "tasks"

    manifest_paths = sorted(tasks_root.glob("*/task.yaml"))
    for manifest_path in manifest_paths:
        task = load_task_manifest(manifest_path)
        assets = load_task_assets(manifest_path)
        computed_metrics = compute_task_manifest_metrics(assets)

        if task.llm_source_line_count != computed_metrics["llm_source_line_count"]:
            raise ValueError(
                f"{task.task_id} llm_source_line_count mismatch: "
                f"manifest={task.llm_source_line_count}, "
                f"computed={computed_metrics['llm_source_line_count']}"
            )
        if task.circuit_gate_count != computed_metrics["circuit_gate_count"]:
            raise ValueError(
                f"{task.task_id} circuit_gate_count mismatch: "
                f"manifest={task.circuit_gate_count}, "
                f"computed={computed_metrics['circuit_gate_count']}"
            )
        print(f"validated {manifest_path.relative_to(project_root)}")

    print(f"validated {len(manifest_paths)} task manifest(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
