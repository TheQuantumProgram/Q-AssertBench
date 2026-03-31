from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class LayoutTests(unittest.TestCase):
    def test_new_package_and_data_layout_exists(self) -> None:
        expected_paths = [
            PROJECT_ROOT / "src" / "qasserbench" / "__init__.py",
            PROJECT_ROOT / "src" / "qasserbench" / "benchmark" / "__init__.py",
            PROJECT_ROOT / "src" / "qasserbench" / "execution" / "__init__.py",
            PROJECT_ROOT / "src" / "qasserbench" / "generation" / "__init__.py",
            PROJECT_ROOT / "src" / "qasserbench" / "evaluation" / "__init__.py",
            PROJECT_ROOT / "src" / "qasserbench" / "reporting" / "__init__.py",
            PROJECT_ROOT / "benchmark_data" / "tasks",
        ]

        for path in expected_paths:
            with self.subTest(path=path):
                self.assertTrue(path.exists(), f"Missing expected path: {path}")


if __name__ == "__main__":
    unittest.main()
