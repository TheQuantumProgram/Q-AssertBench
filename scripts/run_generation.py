"""Run repeated raw-generation trials for selected benchmark tasks."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Sequence

from qasserbench.generation.clients import (
    ModelClient,
    OpenAICompatibleClient,
    StaticResponseClient,
)
from qasserbench.generation.driver import discover_task_manifests, run_generation_trials


def run_generation_experiment(
    *,
    tasks_root: str | Path,
    output_path: str | Path,
    client: ModelClient,
    task_ids: Sequence[str] | None = None,
    trial_count: int = 1,
) -> Path:
    """Run repeated generation for selected tasks and persist raw outputs."""

    manifest_paths = discover_task_manifests(tasks_root, task_ids=task_ids)
    return run_generation_trials(
        manifest_paths=manifest_paths,
        client=client,
        trial_count=trial_count,
        output_path=output_path,
    )


def build_generation_client(args: argparse.Namespace) -> ModelClient:
    client_type = str(args.client)
    if client_type == "static":
        return StaticResponseClient(
            model_name=args.model_id,
            response_text=args.response_text,
        )

    if client_type != "openai-compatible":
        raise ValueError(f"Unsupported client type: {client_type}")

    model_name = args.model or os.environ.get("QAB_MODEL")
    if not model_name:
        raise ValueError("OpenAI-compatible client requires --model or QAB_MODEL.")

    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        raise ValueError(
            f"OpenAI-compatible client requires environment variable {args.api_key_env}."
        )

    api_base_url = args.api_base_url or os.environ.get("QAB_API_BASE_URL")
    return OpenAICompatibleClient(
        model_name=model_name,
        api_key=api_key,
        api_base_url=api_base_url,
        temperature=args.temperature,
        max_output_tokens=args.max_output_tokens,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run repeated raw-generation trials.")
    parser.add_argument("output", type=Path, help="Path to generation_records.jsonl")
    parser.add_argument(
        "--client",
        choices=("static", "openai-compatible"),
        default="static",
        help="Generation client backend",
    )
    parser.add_argument(
        "--tasks-root",
        type=Path,
        default=Path("benchmark_data/tasks"),
        help="Root directory containing task folders with task.yaml files",
    )
    parser.add_argument(
        "--task-id",
        dest="task_ids",
        action="append",
        default=None,
        help="Specific task id to include; may be repeated",
    )
    parser.add_argument("--trials", type=int, default=1, help="Number of repeated trials per task")
    parser.add_argument("--model-id", default="static-model", help="Model identifier to record")
    parser.add_argument("--model", default=None, help="Model name for OpenAI-compatible client")
    parser.add_argument(
        "--api-base-url",
        default=None,
        help="Optional base URL for OpenAI-compatible client; defaults to QAB_API_BASE_URL",
    )
    parser.add_argument(
        "--api-key-env",
        default="QAB_API_KEY",
        help="Environment variable containing the API key for OpenAI-compatible client",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Sampling temperature for OpenAI-compatible generation",
    )
    parser.add_argument(
        "--max-output-tokens",
        type=int,
        default=512,
        help="Maximum completion tokens for OpenAI-compatible generation",
    )
    parser.add_argument(
        "--response-text",
        default="```python\nassert True\n```",
        help="Static response text emitted for every generation trial",
    )
    args = parser.parse_args()

    client = build_generation_client(args)
    output_path = run_generation_experiment(
        tasks_root=args.tasks_root,
        output_path=args.output,
        client=client,
        task_ids=args.task_ids,
        trial_count=args.trials,
    )
    print(f"wrote generation records to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
