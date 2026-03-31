"""Heuristic alignment checks against benchmark gold assertions."""

from __future__ import annotations

from difflib import SequenceMatcher
from typing import Any, Callable

from qasserbench.evaluation.outcomes import AlignmentResult
from qasserbench.execution.interfaces import GoldAssertionResult, TrialExecutionRecord
from qasserbench.generation.artifacts import CandidateAssertionArtifact


def _normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def _build_empty_components() -> dict[str, object]:
    return {
        "structural_score": 0.0,
        "agreement_score": 0.0,
        "assessable_case_count": 0,
        "case_count": 0,
        "agree_count": 0,
        "disagree_case_ids": [],
        "structural_required_ratio": 0.0,
        "structural_optional_ratio": 0.0,
        "structural_similarity": 0.0,
    }


def _structural_components(
    candidate_code: str,
    gold_metadata: dict[str, object] | None,
    gold_code: str | None,
) -> tuple[dict[str, object], tuple[str, ...], tuple[str, ...]]:
    metadata = gold_metadata or {}
    required_terms = tuple(str(term) for term in metadata.get("required_substrings", ()))
    optional_terms = tuple(str(term) for term in metadata.get("optional_substrings", ()))
    normalized_candidate = _normalize_text(candidate_code)

    matched_required = tuple(
        term for term in required_terms if _normalize_text(term) in normalized_candidate
    )
    missing_required = tuple(term for term in required_terms if term not in matched_required)
    matched_optional = tuple(
        term for term in optional_terms if _normalize_text(term) in normalized_candidate
    )

    required_ratio = len(matched_required) / len(required_terms) if required_terms else 0.0
    optional_ratio = len(matched_optional) / len(optional_terms) if optional_terms else 0.0

    similarity = 0.0
    if gold_code:
        similarity = SequenceMatcher(
            None,
            normalized_candidate,
            _normalize_text(gold_code),
        ).ratio()

    weighted_score = 0.0
    weight_total = 0.0
    if required_terms:
        weighted_score += 0.7 * required_ratio
        weight_total += 0.7
    if optional_terms:
        weighted_score += 0.15 * optional_ratio
        weight_total += 0.15
    if gold_code:
        weighted_score += 0.15 * similarity
        weight_total += 0.15
    structural_score = weighted_score / weight_total if weight_total else 0.0

    components = {
        "structural_score": structural_score,
        "agreement_score": 0.0,
        "assessable_case_count": 0,
        "case_count": 0,
        "agree_count": 0,
        "disagree_case_ids": [],
        "structural_required_ratio": required_ratio,
        "structural_optional_ratio": optional_ratio,
        "structural_similarity": similarity,
    }
    return components, matched_required + matched_optional, missing_required


def _candidate_verdict(candidate_passed: bool, candidate_error: str | None) -> str:
    if candidate_error == "runtime_error":
        return "error"
    if candidate_passed:
        return "pass"
    return "fail"


def _agreement_components(
    *,
    trial: TrialExecutionRecord | None,
    gold_evaluator: Callable[[Any], GoldAssertionResult] | None,
) -> dict[str, object]:
    if trial is None or gold_evaluator is None:
        return {
            "agreement_score": 0.0,
            "assessable_case_count": 0,
            "case_count": 0,
            "agree_count": 0,
            "disagree_case_ids": [],
        }

    cases = [
        ("nominal", trial.nominal_execution, trial.nominal_assertion),
        *[
            (
                f"fault:{fault_result.fault_id}",
                fault_result.execution_result,
                fault_result.assertion_result,
            )
            for fault_result in trial.fault_results
        ],
    ]

    agree_count = 0
    assessable_case_count = 0
    disagree_case_ids: list[str] = []

    for case_id, execution_result, assertion_result in cases:
        gold_result = gold_evaluator(execution_result)
        candidate_verdict = _candidate_verdict(
            assertion_result.passed,
            assertion_result.error_type,
        )
        gold_verdict = "pass" if gold_result.passed else "fail"

        if candidate_verdict != "error":
            assessable_case_count += 1

        if candidate_verdict == gold_verdict:
            agree_count += 1
        else:
            disagree_case_ids.append(case_id)

    case_count = len(cases)
    agreement_score = agree_count / case_count if case_count else 0.0
    return {
        "agreement_score": agreement_score,
        "assessable_case_count": assessable_case_count,
        "case_count": case_count,
        "agree_count": agree_count,
        "disagree_case_ids": disagree_case_ids,
    }


def _label_alignment(
    *,
    structural_score: float,
    agreement_score: float,
    required_ratio: float,
    has_structural_evidence: bool,
    has_agreement_evidence: bool,
    matched_terms: tuple[str, ...],
) -> str:
    if not has_structural_evidence and not has_agreement_evidence:
        return "not_assessable"

    if has_agreement_evidence:
        if agreement_score >= 0.85 and structural_score >= 0.45:
            return "aligned"
        if agreement_score >= 0.5 or structural_score >= 0.2 or matched_terms:
            return "partially_aligned"
        return "misaligned"

    if required_ratio == 1.0 and has_structural_evidence:
        return "aligned"
    if matched_terms or structural_score > 0.0:
        return "partially_aligned"
    return "misaligned"


def compare_candidate_to_gold(
    artifact: CandidateAssertionArtifact,
    gold_metadata: dict[str, object] | None,
    gold_code: str | None = None,
    *,
    trial: TrialExecutionRecord | None = None,
    gold_evaluator: Callable[[Any], GoldAssertionResult] | None = None,
) -> AlignmentResult:
    """Compare a candidate artifact with gold metadata and optional gold code."""

    if not artifact.is_usable:
        return AlignmentResult(
            label="not_assessable",
            score=0.0,
            components=_build_empty_components(),
        )

    structural_components, matched_terms, missing_terms = _structural_components(
        artifact.code or "",
        gold_metadata,
        gold_code,
    )
    agreement_components = _agreement_components(
        trial=trial,
        gold_evaluator=gold_evaluator,
    )
    components = dict(structural_components)
    components.update(agreement_components)

    has_structural_evidence = bool(gold_metadata or gold_code)
    has_agreement_evidence = bool(trial is not None and gold_evaluator is not None and components["case_count"])
    structural_score = float(components["structural_score"])
    agreement_score = float(components["agreement_score"])
    required_ratio = float(components["structural_required_ratio"])

    if not has_structural_evidence and not has_agreement_evidence:
        return AlignmentResult(
            label="not_assessable",
            score=0.0,
            components=components,
            matched_terms=matched_terms,
            missing_terms=missing_terms,
        )

    if has_agreement_evidence:
        score = (0.3 * structural_score) + (0.7 * agreement_score)
    else:
        score = structural_score

    label = _label_alignment(
        structural_score=structural_score,
        agreement_score=agreement_score,
        required_ratio=required_ratio,
        has_structural_evidence=has_structural_evidence,
        has_agreement_evidence=has_agreement_evidence,
        matched_terms=matched_terms,
    )

    notes = (
        f"structural={structural_score:.3f}",
        f"agreement={agreement_score:.3f}",
        f"similarity={float(components['structural_similarity']):.3f}",
    )

    return AlignmentResult(
        label=label,
        score=score,
        components=components,
        matched_terms=matched_terms,
        missing_terms=missing_terms,
        notes=notes,
    )
