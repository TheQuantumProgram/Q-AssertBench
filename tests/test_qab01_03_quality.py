from pathlib import Path
import unittest

from qasserbench.benchmark.loader import load_task_assets
from qasserbench.execution.interfaces import ExecutionConfig


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TASKS_ROOT = PROJECT_ROOT / "benchmark_data" / "tasks"
TASK_IDS = ("qab01", "qab02", "qab03")


class QAB0103QualityTests(unittest.TestCase):
    def test_prompts_request_assertion_snippet_without_full_program_wording(self) -> None:
        for task_id in TASK_IDS:
            with self.subTest(task_id=task_id):
                prompt_text = (TASKS_ROOT / task_id / "prompt.md").read_text(encoding="utf-8").lower()

                self.assertIn("assertion", prompt_text)
                self.assertNotIn("complete modified program", prompt_text)

        qab03_prompt = (TASKS_ROOT / "qab03" / "prompt.md").read_text(encoding="utf-8").lower()
        self.assertNotIn("same quantum state", qab03_prompt)
        self.assertIn("measurement", qab03_prompt)

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
                    metadata={"task_id": assets.task.task_id},
                )

                nominal = assets.program.run_program(config)
                nominal_gold = assets.program.evaluate_gold_assertion(nominal)
                self.assertTrue(nominal_gold.passed)

                for fault_id, fault_program in assets.fault_programs.items():
                    fault_result = fault_program.run_program(config)
                    fault_gold = assets.program.evaluate_gold_assertion(fault_result)
                    self.assertFalse(fault_gold.passed, f"{task_id}:{fault_id}")


if __name__ == "__main__":
    unittest.main()
