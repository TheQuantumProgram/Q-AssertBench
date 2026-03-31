from pathlib import Path
import unittest

from qasserbench.benchmark.loader import load_task_assets
from qasserbench.execution.interfaces import ExecutionConfig


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TASKS_ROOT = PROJECT_ROOT / "benchmark_data" / "tasks"
TASK_IDS = ("qab24", "qab25", "qab26", "qab27", "qab28")


class QAB2428QualityTests(unittest.TestCase):
    def test_prompts_start_with_program_summary_and_request_assertion_snippet(self) -> None:
        for task_id in TASK_IDS:
            with self.subTest(task_id=task_id):
                prompt_text = (TASKS_ROOT / task_id / "prompt.md").read_text(encoding="utf-8").strip()
                first_line = prompt_text.splitlines()[0].strip()
                lowered = prompt_text.lower()

                self.assertTrue(first_line.startswith("This program") or first_line.startswith("This circuit"))
                self.assertIn("assertion snippet", lowered)
                self.assertNotIn("complete modified program", lowered)

    def test_task_files_do_not_import_legacy_support(self) -> None:
        for task_id in TASK_IDS:
            with self.subTest(task_id=task_id):
                task_dir = TASKS_ROOT / task_id
                legacy_hits = []
                for path in task_dir.rglob("*.py"):
                    text = path.read_text(encoding="utf-8")
                    if "legacy_support" in text:
                        legacy_hits.append(str(path.relative_to(task_dir)))

                self.assertEqual(legacy_hits, [])

    def test_gold_metadata_required_terms_exist_in_gold_source(self) -> None:
        for task_id in TASK_IDS:
            with self.subTest(task_id=task_id):
                assets = load_task_assets(TASKS_ROOT / task_id / "task.yaml")
                required_terms = tuple(assets.task.gold_metadata.get("required_substrings", ()))

                self.assertTrue(required_terms)
                for term in required_terms:
                    self.assertIn(term, assets.gold_source)

    def test_gold_evaluator_passes_nominal_and_rejects_faults(self) -> None:
        for task_id in TASK_IDS:
            with self.subTest(task_id=task_id):
                assets = load_task_assets(TASKS_ROOT / task_id / "task.yaml")
                config = ExecutionConfig(
                    shots=assets.task.shots,
                    backend="aer_simulator",
                    seed=123,
                    metadata={},
                )

                nominal = assets.program.run_program(config)
                nominal_gold = assets.program.evaluate_gold_assertion(nominal)
                self.assertTrue(nominal_gold.passed)

                for fault_id, fault_program in assets.fault_programs.items():
                    fault_result = fault_program.run_program(config)
                    fault_gold = assets.program.evaluate_gold_assertion(fault_result)
                    self.assertFalse(fault_gold.passed, f"{task_id}:{fault_id}")

    def test_qab24_marks_state_preparation_observation_stage(self) -> None:
        assets = load_task_assets(TASKS_ROOT / "qab24" / "task.yaml")
        result = assets.program.run_program(
            ExecutionConfig(
                shots=assets.task.shots,
                backend="aer_simulator",
                seed=123,
                metadata={},
            )
        )

        self.assertEqual(result.metadata.get("observation_stage"), "after_state_preparation")

    def test_qab27_period_signature_stays_on_expected_peaks(self) -> None:
        assets = load_task_assets(TASKS_ROOT / "qab27" / "task.yaml")
        result = assets.program.run_program(
            ExecutionConfig(
                shots=assets.task.shots,
                backend="aer_simulator",
                seed=123,
                metadata={},
            )
        )

        self.assertEqual(set(result.counts), {"010", "110"})
        self.assertTrue(assets.program.evaluate_gold_assertion(result).passed)


if __name__ == "__main__":
    unittest.main()
