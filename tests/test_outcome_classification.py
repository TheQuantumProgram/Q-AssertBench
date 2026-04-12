import unittest

from qasserbench.evaluation.classify import classify_trial
from qasserbench.evaluation.outcomes import AlignmentResult
from qasserbench.execution.interfaces import (
    AssertionCheckResult,
    ExecutionResult,
    FaultCheckResult,
    TrialExecutionRecord,
)
from qasserbench.generation.extract import extract_candidate_assertion


class OutcomeClassificationTests(unittest.TestCase):
    def test_classifies_nominal_pass_and_fault_detection_as_pass(self) -> None:
        artifact = extract_candidate_assertion(
            'assert counts["00"] > counts["11"]',
            extraction_mode="assertion_block",
        )
        trial = TrialExecutionRecord(
            nominal_execution=ExecutionResult(
                counts={"00": 5, "11": 1},
                shots=6,
                backend="test-backend",
                metadata={},
            ),
            nominal_assertion=AssertionCheckResult(passed=True),
            fault_results=[
                FaultCheckResult(
                    fault_id="fault-1",
                    execution_result=ExecutionResult(
                        counts={"00": 1, "11": 5},
                        shots=6,
                        backend="test-backend",
                        metadata={},
                    ),
                    assertion_result=AssertionCheckResult(
                        passed=False,
                        error_type="assertion_failed",
                    ),
                )
            ],
        )
        alignment = AlignmentResult(label="aligned", score=1.0)

        classification = classify_trial(artifact, trial, alignment)

        self.assertEqual(classification.outcome, "pass")
        self.assertEqual(classification.failure_mode, "none")
        self.assertEqual(classification.alignment_label, "aligned")
        self.assertEqual(classification.fault_detection_rate, 1.0)

    def test_classifies_runtime_error_as_invalid(self) -> None:
        artifact = extract_candidate_assertion(
            "raise RuntimeError('boom')",
            extraction_mode="assertion_block",
        )
        trial = TrialExecutionRecord(
            nominal_execution=ExecutionResult(
                counts={"00": 5, "11": 1},
                shots=6,
                backend="test-backend",
                metadata={},
            ),
            nominal_assertion=AssertionCheckResult(
                passed=False,
                error_type="runtime_error",
                message="boom",
            ),
            fault_results=[],
        )
        alignment = AlignmentResult(label="not_assessable", score=0.0)

        classification = classify_trial(artifact, trial, alignment)

        self.assertEqual(classification.outcome, "invalid")
        self.assertEqual(classification.failure_mode, "invalid")
        self.assertIn("runtime_error", classification.failure_tags)
        self.assertIn("alignment_not_assessable", classification.failure_tags)

    def test_classifies_nominal_assertion_failure_as_nominal_failure(self) -> None:
        artifact = extract_candidate_assertion(
            'assert counts["00"] > counts["11"]',
            extraction_mode="assertion_block",
        )
        trial = TrialExecutionRecord(
            nominal_execution=ExecutionResult(
                counts={"00": 1, "11": 5},
                shots=6,
                backend="test-backend",
                metadata={},
            ),
            nominal_assertion=AssertionCheckResult(
                passed=False,
                error_type="assertion_failed",
            ),
            fault_results=[
                FaultCheckResult(
                    fault_id="fault-1",
                    execution_result=ExecutionResult(
                        counts={"00": 1, "11": 5},
                        shots=6,
                        backend="test-backend",
                        metadata={},
                    ),
                    assertion_result=AssertionCheckResult(
                        passed=False,
                        error_type="assertion_failed",
                    ),
                )
            ],
        )
        alignment = AlignmentResult(label="misaligned", score=0.0)

        classification = classify_trial(artifact, trial, alignment)

        self.assertEqual(classification.outcome, "misjudge")
        self.assertEqual(classification.failure_mode, "nominal_failure")
        self.assertIn("nominal_failure", classification.failure_tags)

    def test_classifies_fault_side_failure_separately_from_nominal_failure(self) -> None:
        artifact = extract_candidate_assertion(
            'assert counts["00"] > counts["11"]',
            extraction_mode="assertion_block",
        )
        trial = TrialExecutionRecord(
            nominal_execution=ExecutionResult(
                counts={"00": 5, "11": 1},
                shots=6,
                backend="test-backend",
                metadata={},
            ),
            nominal_assertion=AssertionCheckResult(passed=True),
            fault_results=[
                FaultCheckResult(
                    fault_id="fault-1",
                    execution_result=ExecutionResult(
                        counts={"00": 5, "11": 1},
                        shots=6,
                        backend="test-backend",
                        metadata={},
                    ),
                    assertion_result=AssertionCheckResult(
                        passed=True,
                        error_type=None,
                    ),
                )
            ],
        )
        alignment = AlignmentResult(label="partially_aligned", score=0.5)

        classification = classify_trial(artifact, trial, alignment)

        self.assertEqual(classification.outcome, "misjudge")
        self.assertEqual(classification.failure_mode, "fault_side_failure")
        self.assertIn("fault_insensitive", classification.failure_tags)


if __name__ == "__main__":
    unittest.main()
