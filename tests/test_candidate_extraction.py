import unittest

from qasserbench.generation.extract import extract_candidate_assertion
from qasserbench.generation.inject import inject_candidate_artifact


class CandidateExtractionTests(unittest.TestCase):
    def test_extracts_python_code_block_as_candidate_artifact(self) -> None:
        artifact = extract_candidate_assertion(
            """
            Here is the assertion block:

            ```python
            assert counts["00"] > counts["11"]
            ```
            """,
            extraction_mode="assertion_block",
        )

        self.assertTrue(artifact.is_usable)
        self.assertEqual(artifact.extraction_mode, "assertion_block")
        self.assertEqual(artifact.code.strip(), 'assert counts["00"] > counts["11"]')
        self.assertEqual(tuple(artifact.diagnostics), ())

    def test_injects_assertion_block_at_marker(self) -> None:
        artifact = extract_candidate_assertion(
            'assert counts["00"] > counts["11"]',
            extraction_mode="assertion_block",
        )
        base_source = "\n".join(
            [
                "def main():",
                "    counts = {'00': 5, '11': 1}",
                "    # ASSERTION_HOOK",
                "",
                "if __name__ == '__main__':",
                "    main()",
            ]
        )

        injected = inject_candidate_artifact(
            base_source,
            artifact,
            insertion_mode="assertion_block",
        )

        self.assertIn('    assert counts["00"] > counts["11"]', injected)
        self.assertNotIn("# ASSERTION_HOOK", injected)

    def test_rejects_unusable_candidate_during_injection(self) -> None:
        artifact = extract_candidate_assertion("", extraction_mode="assertion_block")

        with self.assertRaises(ValueError):
            inject_candidate_artifact(
                "def main():\n    # ASSERTION_HOOK\n",
                artifact,
                insertion_mode="assertion_block",
            )


if __name__ == "__main__":
    unittest.main()
