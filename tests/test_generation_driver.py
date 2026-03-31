from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from qasserbench.generation.clients import GenerationResponse, ModelClient
from qasserbench.generation.driver import (
    discover_task_manifests,
    read_generation_records,
    run_generation_trials,
)
from qasserbench.generation.prompting import COMMON_PROMPT_INTRO, PROMPT_TEMPLATE_VERSION


class FakeModelClient(ModelClient):
    def __init__(self, model_id: str) -> None:
        self._model_id = model_id

    @property
    def model_id(self) -> str:
        return self._model_id

    def generate(self, *, prompt_text: str, task_id: str, trial_index: int) -> GenerationResponse:
        return GenerationResponse(
            text=f"```python\nassert '{task_id}:{trial_index}'\n```",
            payload={
                "task_id": task_id,
                "trial_index": trial_index,
                "prompt_prefix": prompt_text.splitlines()[0],
            },
        )


class GenerationDriverTests(unittest.TestCase):
    def test_writes_repeated_generation_records_with_raw_payload(self) -> None:
        tasks_root = Path("/home/li/project/Q-AssertBench/project_code/benchmark_data/tasks")
        manifest_paths = discover_task_manifests(tasks_root, task_ids=("QAB01", "QAB10"))
        client = FakeModelClient("fake-model")

        with TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "generation_records.jsonl"

            written_path = run_generation_trials(
                manifest_paths=manifest_paths,
                client=client,
                trial_count=2,
                output_path=output_path,
            )
            records = read_generation_records(written_path)

        self.assertEqual(written_path, output_path.resolve())
        self.assertEqual(len(records), 4)

        first = records[0]
        self.assertEqual(first["model_id"], "fake-model")
        self.assertEqual(first["task_id"], "QAB01")
        self.assertEqual(first["trial_index"], 1)
        self.assertIn("raw_response", first)
        self.assertIn("raw_payload", first)
        self.assertEqual(first["raw_payload"]["task_id"], "QAB01")
        self.assertEqual(first["raw_payload"]["prompt_prefix"], COMMON_PROMPT_INTRO)
        self.assertEqual(first["prompt_version"], PROMPT_TEMPLATE_VERSION)
        self.assertIsNone(first["generation_temperature"])
        self.assertIsNone(first["generation_max_output_tokens"])
        self.assertIsNone(first["prompt_tokens"])
        self.assertIsNone(first["completion_tokens"])
        self.assertIsNone(first["total_tokens"])

    def test_filters_tasks_by_requested_task_id(self) -> None:
        tasks_root = Path("/home/li/project/Q-AssertBench/project_code/benchmark_data/tasks")
        manifest_paths = discover_task_manifests(tasks_root, task_ids=("QAB20",))
        client = FakeModelClient("fake-model")

        with TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "generation_records.jsonl"
            records = read_generation_records(
                run_generation_trials(
                    manifest_paths=manifest_paths,
                    client=client,
                    trial_count=3,
                    output_path=output_path,
                )
            )

        self.assertEqual(len(records), 3)
        self.assertEqual({record["task_id"] for record in records}, {"QAB20"})
        self.assertEqual([record["trial_index"] for record in records], [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
