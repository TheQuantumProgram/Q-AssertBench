from pathlib import Path
from tempfile import TemporaryDirectory
import textwrap
import unittest

from qasserbench.benchmark.loader import load_task_manifest
from qasserbench.benchmark.schema import BenchmarkTask


class TaskLoaderTests(unittest.TestCase):
    def test_loads_valid_manifest_and_resolves_prompt_path(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            task_dir = Path(tmp_dir)
            (task_dir / "prompt.md").write_text("Prompt text\n", encoding="utf-8")
            (task_dir / "task.yaml").write_text(
                textwrap.dedent(
                    """
                    task_id: QAB01
                    title: Superposition and classical state mix
                    family: basic_behavior
                    property_type: distribution
                    qubit_count: 5
                    shots: 1024
                    llm_source_line_count: 18
                    circuit_gate_count: 9
                    program_entry: program.py:build_program
                    gold_entry: gold.py:evaluate_gold
                    gold_compare_mode: hybrid
                    gold_metadata:
                      expected_observables:
                        - bit_occurrences
                      target_qubits:
                        - 0
                        - 1
                    fault_variants:
                      - id: missing_classical_state
                        path: faults/missing_classical_state.py
                    insertion_mode: inline_program_rewrite
                    prompt_file: prompt.md
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            task = load_task_manifest(task_dir / "task.yaml")

        self.assertIsInstance(task, BenchmarkTask)
        self.assertEqual(task.task_id, "QAB01")
        self.assertEqual(task.gold_compare_mode, "hybrid")
        self.assertEqual(task.prompt_path.name, "prompt.md")
        self.assertEqual(task.fault_variants[0]["id"], "missing_classical_state")
        self.assertEqual(task.gold_metadata["target_qubits"], [0, 1])
        self.assertEqual(task.llm_source_line_count, 18)
        self.assertEqual(task.circuit_gate_count, 9)

    def test_rejects_manifest_missing_required_fields(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            task_dir = Path(tmp_dir)
            (task_dir / "task.yaml").write_text(
                textwrap.dedent(
                    """
                    task_id: QAB02
                    title: Missing gold metadata example
                    family: basic_behavior
                    property_type: distribution
                    qubit_count: 3
                    shots: 256
                    program_entry: program.py:build_program
                    gold_entry: gold.py:evaluate_gold
                    insertion_mode: inline_program_rewrite
                    prompt_file: prompt.md
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                load_task_manifest(task_dir / "task.yaml")


if __name__ == "__main__":
    unittest.main()
