import unittest

from qasserbench.execution.interfaces import (
    ExecutionConfig,
    ExecutionResult,
    GoldAssertionResult,
    ProgramDefinition,
)
from qasserbench.execution.runtime import normalize_counts


class RuntimeInterfaceTests(unittest.TestCase):
    def test_runtime_interfaces_support_normalized_execution_flow(self) -> None:
        def build_program() -> str:
            return "program-object"

        def run_program(config: ExecutionConfig) -> ExecutionResult:
            return ExecutionResult(
                counts=normalize_counts({"10": 2, "00": 5}),
                shots=config.shots,
                backend=config.backend,
                metadata=dict(config.metadata),
            )

        def evaluate_gold_assertion(result: ExecutionResult) -> GoldAssertionResult:
            return GoldAssertionResult(
                passed=result.counts["00"] > result.counts["10"],
                details={"dominant_state": "00"},
            )

        program = ProgramDefinition(
            task_id="QAB01",
            build_program=build_program,
            run_program=run_program,
            evaluate_gold_assertion=evaluate_gold_assertion,
        )
        config = ExecutionConfig(
            shots=7,
            backend="aer_simulator",
            seed=13,
            metadata={"task_id": "QAB01"},
        )

        built_program = program.build_program()
        result = program.run_program(config)
        gold_result = program.evaluate_gold_assertion(result)

        self.assertEqual(built_program, "program-object")
        self.assertEqual(result.counts, {"00": 5, "10": 2})
        self.assertEqual(result.shots, 7)
        self.assertEqual(result.backend, "aer_simulator")
        self.assertEqual(result.metadata["task_id"], "QAB01")
        self.assertTrue(gold_result.passed)
        self.assertEqual(gold_result.details["dominant_state"], "00")


if __name__ == "__main__":
    unittest.main()
