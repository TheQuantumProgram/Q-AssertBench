import unittest

from qasserbench.evaluation.alignment import compare_candidate_to_gold
from qasserbench.execution.interfaces import (
    AssertionCheckResult,
    ExecutionResult,
    FaultCheckResult,
    GoldAssertionResult,
    TrialExecutionRecord,
)
from qasserbench.generation.extract import extract_candidate_assertion


def _build_execution_result(case_id: str, gold_passed: bool) -> ExecutionResult:
    return ExecutionResult(
        counts={case_id: 1},
        shots=128,
        backend="test_backend",
        metadata={"case_id": case_id, "gold_passed": gold_passed},
    )


def _build_assertion_result(status: str) -> AssertionCheckResult:
    if status == "pass":
        return AssertionCheckResult(passed=True)
    if status == "fail":
        return AssertionCheckResult(
            passed=False,
            error_type="assertion_failed",
            message="assertion failed",
        )
    if status == "error":
        return AssertionCheckResult(
            passed=False,
            error_type="runtime_error",
            message="runtime error",
        )
    raise ValueError(f"Unsupported assertion status: {status}")


def _build_trial(
    *,
    nominal_status: str,
    nominal_gold_passed: bool,
    fault_statuses: tuple[str, ...],
    fault_gold_passed: tuple[bool, ...],
) -> TrialExecutionRecord:
    fault_results = [
        FaultCheckResult(
            fault_id=f"fault_{index + 1}",
            execution_result=_build_execution_result(
                case_id=f"fault_{index + 1}",
                gold_passed=gold_passed,
            ),
            assertion_result=_build_assertion_result(status),
        )
        for index, (status, gold_passed) in enumerate(zip(fault_statuses, fault_gold_passed))
    ]
    return TrialExecutionRecord(
        nominal_execution=_build_execution_result("nominal", nominal_gold_passed),
        nominal_assertion=_build_assertion_result(nominal_status),
        fault_results=fault_results,
    )


def _gold_evaluator(result: ExecutionResult) -> GoldAssertionResult:
    return GoldAssertionResult(passed=bool(result.metadata["gold_passed"]))


class GoldAlignmentTests(unittest.TestCase):
    def test_marks_fully_matching_and_agreeing_candidate_as_aligned(self) -> None:
        artifact = extract_candidate_assertion(
            """
            bit_occurrences = []
            assert any(len(bits) == 1 for bits in bit_occurrences)
            assert any(len(bits) == 2 for bits in bit_occurrences)
            """,
            extraction_mode="assertion_block",
        )
        trial = _build_trial(
            nominal_status="pass",
            nominal_gold_passed=True,
            fault_statuses=("fail",),
            fault_gold_passed=(False,),
        )
        alignment = compare_candidate_to_gold(
            artifact,
            gold_metadata={
                "required_substrings": [
                    "len(bits) == 1",
                    "len(bits) == 2",
                ],
                "optional_substrings": ["bit_occurrences"],
            },
            gold_code="assert any(len(bits) == 1 for bits in bit_occurrences)",
            trial=trial,
            gold_evaluator=_gold_evaluator,
        )

        self.assertEqual(alignment.label, "aligned")
        self.assertEqual(alignment.missing_terms, ())
        self.assertAlmostEqual(alignment.components["agreement_score"], 1.0)
        self.assertGreater(alignment.components["structural_score"], 0.9)

    def test_downgrades_structurally_similar_but_disagreeing_candidate(self) -> None:
        artifact = extract_candidate_assertion(
            """
            bit_occurrences = []
            assert any(len(bits) == 1 for bits in bit_occurrences)
            assert any(len(bits) == 2 for bits in bit_occurrences)
            """,
            extraction_mode="assertion_block",
        )
        trial = _build_trial(
            nominal_status="pass",
            nominal_gold_passed=True,
            fault_statuses=("pass",),
            fault_gold_passed=(False,),
        )
        alignment = compare_candidate_to_gold(
            artifact,
            gold_metadata={
                "required_substrings": [
                    "len(bits) == 1",
                    "len(bits) == 2",
                ],
                "optional_substrings": ["bit_occurrences"],
            },
            gold_code="assert any(len(bits) == 1 for bits in bit_occurrences)",
            trial=trial,
            gold_evaluator=_gold_evaluator,
        )

        self.assertEqual(alignment.label, "partially_aligned")
        self.assertAlmostEqual(alignment.components["agreement_score"], 0.5)
        self.assertIn("fault:fault_1", alignment.components["disagree_case_ids"])
        self.assertLess(alignment.score, 1.0)

    def test_grants_partial_credit_for_behavioral_agreement_with_weak_structure(self) -> None:
        artifact = extract_candidate_assertion(
            "assert counts.get('nominal', 0) >= 0",
            extraction_mode="assertion_block",
        )
        trial = _build_trial(
            nominal_status="pass",
            nominal_gold_passed=True,
            fault_statuses=("fail", "fail"),
            fault_gold_passed=(False, False),
        )
        alignment = compare_candidate_to_gold(
            artifact,
            gold_metadata={
                "required_substrings": ["len(bits) == 1"],
                "optional_substrings": ["bit_occurrences"],
            },
            gold_code="assert any(len(bits) == 1 for bits in bit_occurrences)",
            trial=trial,
            gold_evaluator=_gold_evaluator,
        )

        self.assertEqual(alignment.label, "partially_aligned")
        self.assertAlmostEqual(alignment.components["agreement_score"], 1.0)
        self.assertLess(alignment.components["structural_score"], 0.3)
        self.assertGreater(alignment.score, 0.5)

    def test_marks_empty_candidate_as_not_assessable(self) -> None:
        artifact = extract_candidate_assertion("", extraction_mode="assertion_block")
        alignment = compare_candidate_to_gold(
            artifact,
            gold_metadata={"required_substrings": ["len(bits) == 1"]},
            trial=_build_trial(
                nominal_status="pass",
                nominal_gold_passed=True,
                fault_statuses=("fail",),
                fault_gold_passed=(False,),
            ),
            gold_evaluator=_gold_evaluator,
        )

        self.assertEqual(alignment.label, "not_assessable")
        self.assertEqual(alignment.score, 0.0)
        self.assertEqual(alignment.components["agreement_score"], 0.0)


if __name__ == "__main__":
    unittest.main()
