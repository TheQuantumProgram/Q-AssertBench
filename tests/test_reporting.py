from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from qasserbench.reporting.aggregate import aggregate_trial_results
from qasserbench.reporting.io import read_trial_results, write_trial_results


class ReportingTests(unittest.TestCase):
    def test_writes_and_reads_trial_level_jsonl_records(self) -> None:
        records = [
            {
                "model_id": "model-a",
                "task_id": "QAB01",
                "task_category": "distributional_behavior",
                "trial_index": 1,
                "outcome": "pass",
                "alignment_label": "aligned",
            },
            {
                "model_id": "model-a",
                "task_id": "QAB02",
                "task_category": "entanglement_correlation",
                "trial_index": 1,
                "outcome": "misjudge",
                "alignment_label": "misaligned",
            },
        ]

        with TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "trial_results.jsonl"
            write_trial_results(records, output_path)

            self.assertTrue(output_path.exists())
            self.assertEqual(len(output_path.read_text(encoding="utf-8").strip().splitlines()), 2)

            loaded = read_trial_results(output_path)

        self.assertEqual(loaded, records)

    def test_aggregates_model_pass_at_k_and_alignment_counts(self) -> None:
        records = [
            {
                "model_id": "model-a",
                "task_id": "QAB01",
                "task_category": "distributional_behavior",
                "trial_index": 1,
                "outcome": "misjudge",
                "alignment_label": "partially_aligned",
            },
            {
                "model_id": "model-a",
                "task_id": "QAB01",
                "task_category": "distributional_behavior",
                "trial_index": 2,
                "outcome": "pass",
                "alignment_label": "aligned",
            },
            {
                "model_id": "model-a",
                "task_id": "QAB02",
                "task_category": "entanglement_correlation",
                "trial_index": 1,
                "outcome": "pass",
                "alignment_label": "aligned",
            },
            {
                "model_id": "model-b",
                "task_id": "QAB01",
                "task_category": "distributional_behavior",
                "trial_index": 1,
                "outcome": "invalid",
                "alignment_label": "not_assessable",
            },
        ]

        summary = aggregate_trial_results(records, pass_k_values=(1, 2))

        self.assertIn("model_summaries", summary)
        self.assertIn("task_summaries", summary)
        self.assertIn("category_summaries", summary)
        self.assertIn("alignment_summaries", summary)

        model_a = next(item for item in summary["model_summaries"] if item["model_id"] == "model-a")
        self.assertEqual(model_a["trial_count"], 3)
        self.assertAlmostEqual(model_a["pass_rate"], 2 / 3)
        self.assertAlmostEqual(model_a["pass@1"], 0.5)
        self.assertAlmostEqual(model_a["pass@2"], 1.0)
        self.assertEqual(model_a["alignment_counts"]["aligned"], 2)
        self.assertEqual(model_a["alignment_counts"]["partially_aligned"], 1)

        category_summary = next(
            item
            for item in summary["category_summaries"]
            if item["model_id"] == "model-a" and item["task_category"] == "distributional_behavior"
        )
        self.assertEqual(category_summary["trial_count"], 2)

        serialized = json.dumps(summary)
        self.assertIn("pass@2", serialized)


if __name__ == "__main__":
    unittest.main()
