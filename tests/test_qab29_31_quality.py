from pathlib import Path
import unittest

from qasserbench.benchmark.loader import load_task_assets
from qasserbench.execution.interfaces import ExecutionConfig


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TASKS_ROOT = PROJECT_ROOT / "benchmark_data" / "tasks"
TASK_IDS = ("qab29", "qab30", "qab31")


class QAB2931QualityTests(unittest.TestCase):
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

    def test_qab29_gold_evaluator_passes_nominal_and_rejects_fault(self) -> None:
        assets = load_task_assets(TASKS_ROOT / "qab29" / "task.yaml")
        config = ExecutionConfig(
            shots=256,
            backend="aer_simulator",
            seed=123,
            metadata={},
        )

        nominal = assets.program.run_program(config)
        faulty = next(iter(assets.fault_programs.values())).run_program(config)

        self.assertTrue(assets.program.evaluate_gold_assertion(nominal).passed)
        self.assertFalse(assets.program.evaluate_gold_assertion(faulty).passed)

    def test_qab30_gold_evaluator_passes_nominal_and_rejects_fault(self) -> None:
        assets = load_task_assets(TASKS_ROOT / "qab30" / "task.yaml")
        config = ExecutionConfig(
            shots=assets.task.shots,
            backend="aer_simulator",
            seed=123,
            metadata={},
        )

        nominal = assets.program.run_program(config)
        faulty = next(iter(assets.fault_programs.values())).run_program(config)

        self.assertTrue(assets.program.evaluate_gold_assertion(nominal).passed)
        self.assertFalse(assets.program.evaluate_gold_assertion(faulty).passed)

    def test_qab31_uses_logical_search_qubit_count(self) -> None:
        assets = load_task_assets(TASKS_ROOT / "qab31" / "task.yaml")
        self.assertEqual(assets.task.qubit_count, 15)

    def test_qab31_gold_evaluator_passes_nominal_and_rejects_fault(self) -> None:
        assets = load_task_assets(TASKS_ROOT / "qab31" / "task.yaml")
        config = ExecutionConfig(
            shots=512,
            backend="aer_simulator",
            seed=123,
            metadata={},
        )

        nominal = assets.program.run_program(config)
        faulty = next(iter(assets.fault_programs.values())).run_program(config)

        self.assertTrue(assets.program.evaluate_gold_assertion(nominal).passed)
        self.assertFalse(assets.program.evaluate_gold_assertion(faulty).passed)


if __name__ == "__main__":
    unittest.main()
