from pathlib import Path
import unittest

from qasserbench.benchmark.loader import load_task_assets
from qasserbench.evaluation.alignment import compare_candidate_to_gold
from qasserbench.evaluation.classify import classify_trial
from qasserbench.execution.interfaces import ExecutionConfig
from qasserbench.execution.runner import run_candidate_trial
from qasserbench.generation.extract import extract_candidate_assertion


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TASKS_ROOT = PROJECT_ROOT / "benchmark_data" / "tasks"
PILOT_TASK_IDS = ("qab01", "qab10", "qab20")
FLATTENED_TASK_IDS = ("qab02", "qab03", "qab20")


class PilotTaskTests(unittest.TestCase):
    def test_loads_pilot_task_assets(self) -> None:
        for task_id in PILOT_TASK_IDS:
            with self.subTest(task_id=task_id):
                assets = load_task_assets(TASKS_ROOT / task_id / "task.yaml")

                self.assertEqual(assets.task.task_id.lower(), task_id)
                self.assertTrue(assets.prompt_text.strip())
                self.assertTrue(assets.gold_source.strip())
                self.assertGreaterEqual(len(assets.fault_programs), 1)
                self.assertEqual(assets.program.task_id, assets.task.task_id)

    def test_gold_candidate_passes_nominal_and_detects_faults(self) -> None:
        for task_id in PILOT_TASK_IDS:
            with self.subTest(task_id=task_id):
                assets = load_task_assets(TASKS_ROOT / task_id / "task.yaml")
                artifact = extract_candidate_assertion(
                    assets.gold_source,
                    extraction_mode="assertion_block",
                )

                trial = run_candidate_trial(
                    program=assets.program,
                    fault_programs=assets.fault_programs,
                    artifact=artifact,
                    config=ExecutionConfig(
                        shots=assets.task.shots,
                        backend="aer_simulator",
                        seed=123,
                        metadata={"task_id": assets.task.task_id},
                    ),
                )
                alignment = compare_candidate_to_gold(
                    artifact,
                    assets.task.gold_metadata,
                    assets.gold_source,
                    trial=trial,
                    gold_evaluator=assets.program.evaluate_gold_assertion,
                )
                classification = classify_trial(artifact, trial, alignment)

                self.assertEqual(alignment.label, "aligned")
                self.assertEqual(classification.outcome, "pass")

    def test_flattened_representative_tasks_still_run_end_to_end(self) -> None:
        for task_id in FLATTENED_TASK_IDS:
            with self.subTest(task_id=task_id):
                assets = load_task_assets(TASKS_ROOT / task_id / "task.yaml")
                artifact = extract_candidate_assertion(
                    assets.gold_source,
                    extraction_mode="assertion_block",
                )

                trial = run_candidate_trial(
                    program=assets.program,
                    fault_programs=assets.fault_programs,
                    artifact=artifact,
                    config=ExecutionConfig(
                        shots=assets.task.shots,
                        backend="aer_simulator",
                        seed=123,
                        metadata={"task_id": assets.task.task_id},
                    ),
                )
                alignment = compare_candidate_to_gold(
                    artifact,
                    assets.task.gold_metadata,
                    assets.gold_source,
                    trial=trial,
                    gold_evaluator=assets.program.evaluate_gold_assertion,
                )

                self.assertEqual(alignment.label, "aligned")
                self.assertTrue(trial.nominal_assertion.passed)


if __name__ == "__main__":
    unittest.main()
