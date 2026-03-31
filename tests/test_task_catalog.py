from pathlib import Path
import unittest

from qasserbench.benchmark.loader import load_task_assets
from qasserbench.generation.driver import discover_task_manifests
from scripts.validate_tasks import compute_task_manifest_metrics


class TaskCatalogTests(unittest.TestCase):
    def test_full_task_catalog_loads_and_validates(self) -> None:
        tasks_root = Path("/home/li/project/Q-AssertBench/project_code/benchmark_data/tasks")
        manifest_paths = discover_task_manifests(tasks_root)

        self.assertEqual(len(manifest_paths), 37)

        loaded_assets = [load_task_assets(manifest_path) for manifest_path in manifest_paths]
        task_ids = [assets.task.task_id for assets in loaded_assets]

        self.assertEqual(task_ids, [f"QAB{index:02d}" for index in range(1, 38)])

        for assets in loaded_assets:
            self.assertTrue(assets.prompt_text.strip(), assets.task.task_id)
            self.assertTrue(assets.gold_source.strip(), assets.task.task_id)
            self.assertGreaterEqual(len(assets.fault_programs), 1, assets.task.task_id)
            self.assertEqual(assets.program.task_id, assets.task.task_id)

    def test_project_root_uses_new_catalog_layout(self) -> None:
        project_root = Path("/home/li/project/Q-AssertBench/project_code")
        legacy_root = project_root / "Q-AssertBench(old)"
        readme_path = project_root / "README.md"

        self.assertFalse(legacy_root.exists())
        self.assertTrue(readme_path.exists())

        readme_text = readme_path.read_text(encoding="utf-8")
        self.assertIn("benchmark_data/tasks", readme_text)
        self.assertIn("scripts/run_generation.py", readme_text)
        self.assertIn("scripts/run_evaluation.py", readme_text)

    def test_all_tasks_use_flat_single_layer_assets(self) -> None:
        tasks_root = Path("/home/li/project/Q-AssertBench/project_code/benchmark_data/tasks")

        for task_dir in sorted(path for path in tasks_root.iterdir() if path.is_dir()):
            task_id = task_dir.name
            with self.subTest(task_id=task_id):
                legacy_files = sorted(
                    str(path.relative_to(task_dir))
                    for path in task_dir.rglob("legacy*.py")
                )
                self.assertEqual(legacy_files, [])

                if (task_dir / "program.py").exists():
                    program_text = (task_dir / "program.py").read_text(encoding="utf-8")
                    self.assertIn("def build_circuit(", program_text)
                    self.assertIn("def run_program(", program_text)

    def test_repository_gitignore_covers_python_cache_artifacts(self) -> None:
        gitignore_path = Path("/home/li/project/Q-AssertBench/project_code/.gitignore")
        gitignore_text = gitignore_path.read_text(encoding="utf-8")

        self.assertIn("__pycache__/", gitignore_text)
        self.assertIn("*.py[cod]", gitignore_text)

    def test_repository_tree_avoids_deprecated_qasm_simulator_alias(self) -> None:
        project_root = Path("/home/li/project/Q-AssertBench/project_code")
        deprecated_hits = []
        source_roots = [
            project_root / "benchmark_data",
            project_root / "scripts",
            project_root / "src",
        ]

        for source_root in source_roots:
            for path in source_root.rglob("*.py"):
                if path == project_root / "src/qasserbench/execution/backends.py":
                    continue
                text = path.read_text(encoding="utf-8")
                if "qasm_simulator" in text:
                    deprecated_hits.append(str(path.relative_to(project_root)))

        self.assertEqual(deprecated_hits, [])

    def test_all_tasks_declare_validated_prompt_and_circuit_metrics(self) -> None:
        tasks_root = Path("/home/li/project/Q-AssertBench/project_code/benchmark_data/tasks")

        for manifest_path in sorted(tasks_root.glob("*/task.yaml")):
            assets = load_task_assets(manifest_path)
            with self.subTest(task_id=assets.task.task_id):
                computed_metrics = compute_task_manifest_metrics(assets)

                self.assertEqual(
                    assets.task.llm_source_line_count,
                    computed_metrics["llm_source_line_count"],
                )
                self.assertEqual(
                    assets.task.circuit_gate_count,
                    computed_metrics["circuit_gate_count"],
                )
                self.assertGreater(assets.task.llm_source_line_count, 0)
                self.assertGreater(assets.task.circuit_gate_count, 0)

    def test_shot_counts_follow_repository_policy(self) -> None:
        tasks_root = Path("/home/li/project/Q-AssertBench/project_code/benchmark_data/tasks")
        high_shot_tasks: dict[str, int] = {}

        for manifest_path in sorted(tasks_root.glob("*/task.yaml")):
            assets = load_task_assets(manifest_path)
            self.assertLessEqual(assets.task.shots, 2048, assets.task.task_id)
            if assets.task.shots > 1024:
                high_shot_tasks[assets.task.task_id] = assets.task.shots

        self.assertEqual(high_shot_tasks, {"QAB34": 2048})


if __name__ == "__main__":
    unittest.main()
