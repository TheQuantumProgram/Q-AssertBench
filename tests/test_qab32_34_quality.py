from pathlib import Path
import ast
import unittest

from qasserbench.benchmark.loader import load_task_assets
from qasserbench.execution.interfaces import ExecutionConfig
from qasserbench.generation.prompting import inspect_task_prompt


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TASKS_ROOT = PROJECT_ROOT / "benchmark_data" / "tasks"
TASK_IDS = ("qab32", "qab33", "qab34")


class QAB3234QualityTests(unittest.TestCase):
    def test_prompts_start_with_program_summary_and_request_assertion_snippet(self) -> None:
        for task_id in TASK_IDS:
            with self.subTest(task_id=task_id):
                prompt_text = (TASKS_ROOT / task_id / "prompt.md").read_text(encoding="utf-8").strip()
                first_line = prompt_text.splitlines()[0].strip()
                lowered = prompt_text.lower()

                self.assertTrue(first_line.startswith("This program") or first_line.startswith("This circuit"))
                self.assertIn("assertion snippet", lowered)
                self.assertNotIn("complete modified program", lowered)

    def test_gold_metadata_required_terms_exist_in_gold_source(self) -> None:
        for task_id in TASK_IDS:
            with self.subTest(task_id=task_id):
                assets = load_task_assets(TASKS_ROOT / task_id / "task.yaml")
                required_terms = tuple(assets.task.gold_metadata.get("required_substrings", ()))

                self.assertTrue(required_terms)
                for term in required_terms:
                    self.assertIn(term, assets.gold_source)

    def test_prompt_rendering_exposes_long_source_context(self) -> None:
        minimum_build_circuit_lines = {
            "qab32": 100,
            "qab33": 200,
            "qab34": 300,
        }
        for task_id in TASK_IDS:
            with self.subTest(task_id=task_id):
                assets = load_task_assets(TASKS_ROOT / task_id / "task.yaml")
                context = inspect_task_prompt(assets)
                program_source = (TASKS_ROOT / task_id / "program.py").read_text(encoding="utf-8")
                program_module = ast.parse(program_source)
                build_circuit_node = next(
                    node
                    for node in program_module.body
                    if isinstance(node, ast.FunctionDef) and node.name == "build_circuit"
                )
                build_circuit_lines = build_circuit_node.end_lineno - build_circuit_node.lineno + 1

                self.assertEqual(context.selected_function_names, ("build_circuit", "run_program"))
                self.assertIn("def build_circuit(", context.source_excerpt)
                self.assertIn("def run_program(", context.source_excerpt)
                self.assertGreaterEqual(build_circuit_lines, minimum_build_circuit_lines[task_id])

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
                self.assertTrue(nominal_gold.passed, task_id)

                for fault_id, fault_program in assets.fault_programs.items():
                    fault_result = fault_program.run_program(config)
                    fault_gold = assets.program.evaluate_gold_assertion(fault_result)
                    self.assertFalse(fault_gold.passed, f"{task_id}:{fault_id}")


if __name__ == "__main__":
    unittest.main()
