from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from qasserbench.reporting.io import read_trial_results
from scripts.run_evaluation import evaluate_generation_records


class EvaluationPipelineTests(unittest.TestCase):
    def test_evaluates_records_after_redundant_experiment_fields_are_removed(self) -> None:
        tasks_root = Path("/home/li/project/Q-AssertBench/project_code/benchmark_data/tasks")

        with TemporaryDirectory() as tmp_dir:
            input_path = Path(tmp_dir) / "generation_records.jsonl"
            output_path = Path(tmp_dir) / "trial_results.jsonl"
            input_path.write_text(
                json.dumps(
                    {
                        "model_id": "static-model",
                        "provider_model_id": "static-model",
                        "task_id": "QAB01",
                        "trial_index": 1,
                        "raw_response": "```python\nassert sum(counts.values()) == shots\n```",
                        "raw_payload": {},
                        "generation_temperature": 0.0,
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            evaluate_generation_records(
                input_path=input_path,
                output_path=output_path,
                tasks_root=tasks_root,
            )
            records = read_trial_results(output_path)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["task_id"], "QAB01")
        self.assertNotIn("manifest_path", records[0])
        self.assertNotIn("generation_max_output_tokens", records[0])


if __name__ == "__main__":
    unittest.main()
