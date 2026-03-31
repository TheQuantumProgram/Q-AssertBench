from pathlib import Path
import unittest

from qasserbench.benchmark.loader import load_task_assets
from qasserbench.execution.interfaces import ExecutionConfig
from qasserbench.generation.driver import discover_task_manifests


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TASKS_ROOT = PROJECT_ROOT / "benchmark_data" / "tasks"


class PreExperimentReadinessTests(unittest.TestCase):
    def test_all_tasks_execute_and_gold_checks_behave_as_expected(self) -> None:
        manifest_paths = discover_task_manifests(TASKS_ROOT)

        for manifest_path in manifest_paths:
            assets = load_task_assets(manifest_path)
            config = ExecutionConfig(
                shots=assets.task.shots,
                backend="aer_simulator",
                seed=123,
                metadata={"task_id": assets.task.task_id},
            )

            with self.subTest(task_id=assets.task.task_id, phase="nominal_execution"):
                nominal = assets.program.run_program(config)
                self.assertTrue(nominal.counts)
                self.assertEqual(nominal.shots, config.shots)
                self.assertEqual(nominal.backend, config.backend)

            with self.subTest(task_id=assets.task.task_id, phase="nominal_gold"):
                nominal_gold = assets.program.evaluate_gold_assertion(nominal)
                self.assertTrue(nominal_gold.passed, assets.task.task_id)

            with self.subTest(task_id=assets.task.task_id, phase="fault_catalog"):
                self.assertTrue(assets.fault_programs, assets.task.task_id)

            for fault_id, fault_program in assets.fault_programs.items():
                with self.subTest(task_id=assets.task.task_id, phase="fault_execution", fault_id=fault_id):
                    fault_result = fault_program.run_program(config)
                    self.assertTrue(fault_result.counts)
                    self.assertEqual(fault_result.shots, config.shots)
                    self.assertEqual(fault_result.backend, config.backend)

                with self.subTest(task_id=assets.task.task_id, phase="fault_gold", fault_id=fault_id):
                    fault_gold = assets.program.evaluate_gold_assertion(fault_result)
                    self.assertFalse(fault_gold.passed, f"{assets.task.task_id}:{fault_id}")


if __name__ == "__main__":
    unittest.main()
