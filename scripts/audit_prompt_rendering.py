"""Audit prompt rendering compatibility for all benchmark tasks."""

from __future__ import annotations

from pathlib import Path

from qasserbench.benchmark.loader import load_task_assets
from qasserbench.generation.prompting import inspect_task_prompt, render_task_prompt


def main() -> int:
    tasks_root = Path("benchmark_data/tasks").resolve()
    manifest_paths = sorted(tasks_root.glob("*/task.yaml"))

    for manifest_path in manifest_paths:
        assets = load_task_assets(manifest_path)
        context = inspect_task_prompt(assets)
        rendered_prompt = render_task_prompt(assets)
        probes = ",".join(context.probe_function_names) if context.probe_function_names else "-"
        stage = context.observation_stage or "-"
        functions = ",".join(context.selected_function_names)
        print(
            " | ".join(
                [
                    assets.task.task_id,
                    f"version={context.prompt_version}",
                    f"stage={stage}",
                    f"probes={probes}",
                    f"functions={functions}",
                    f"prompt_chars={len(rendered_prompt)}",
                ]
            )
        )

    print(f"audited {len(manifest_paths)} task prompt(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
