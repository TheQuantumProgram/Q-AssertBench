"""Aggregation helpers for benchmark trial records."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any


def _sorted_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        records,
        key=lambda item: (
            str(item.get("model_id", "")),
            str(item.get("task_id", "")),
            int(item.get("trial_index", 0)),
        ),
    )


def _pass_at_k(records: list[dict[str, Any]], k: int) -> float:
    by_task: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in _sorted_records(records):
        by_task[str(record["task_id"])].append(record)

    if not by_task:
        return 0.0

    successes = 0
    for task_records in by_task.values():
        limited = [record for record in task_records if int(record.get("trial_index", 0)) <= k]
        if any(record.get("outcome") == "pass" for record in limited):
            successes += 1
    return successes / len(by_task)


def _alignment_counts(records: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(str(record.get("alignment_label", "unknown")) for record in records)
    return dict(sorted(counts.items(), key=lambda item: item[0]))


def _summarize_group(base_fields: dict[str, Any], records: list[dict[str, Any]], pass_k_values: tuple[int, ...]) -> dict[str, Any]:
    trial_count = len(records)
    pass_count = sum(1 for record in records if record.get("outcome") == "pass")
    summary: dict[str, Any] = dict(base_fields)
    summary["trial_count"] = trial_count
    summary["pass_count"] = pass_count
    summary["pass_rate"] = (pass_count / trial_count) if trial_count else 0.0
    summary["alignment_counts"] = _alignment_counts(records)
    for k in pass_k_values:
        summary[f"pass@{k}"] = _pass_at_k(records, k)
    return summary


def aggregate_trial_results(
    records: list[dict[str, Any]],
    pass_k_values: tuple[int, ...] = (1, 5),
) -> dict[str, list[dict[str, Any]]]:
    """Aggregate trial-level records into model/task/category/alignment summaries."""

    model_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    task_groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    category_groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    alignment_groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)

    for record in records:
        model_id = str(record["model_id"])
        task_id = str(record["task_id"])
        task_category = str(record.get("task_category", "unknown"))
        alignment_label = str(record.get("alignment_label", "unknown"))

        model_groups[model_id].append(record)
        task_groups[(model_id, task_id)].append(record)
        category_groups[(model_id, task_category)].append(record)
        alignment_groups[(model_id, alignment_label)].append(record)

    model_summaries = [
        _summarize_group({"model_id": model_id}, group_records, pass_k_values)
        for model_id, group_records in sorted(model_groups.items())
    ]
    task_summaries = [
        _summarize_group(
            {"model_id": model_id, "task_id": task_id},
            group_records,
            pass_k_values,
        )
        for (model_id, task_id), group_records in sorted(task_groups.items())
    ]
    category_summaries = [
        _summarize_group(
            {"model_id": model_id, "task_category": task_category},
            group_records,
            pass_k_values,
        )
        for (model_id, task_category), group_records in sorted(category_groups.items())
    ]
    alignment_summaries = [
        _summarize_group(
            {"model_id": model_id, "alignment_label": alignment_label},
            group_records,
            pass_k_values,
        )
        for (model_id, alignment_label), group_records in sorted(alignment_groups.items())
    ]

    return {
        "model_summaries": model_summaries,
        "task_summaries": task_summaries,
        "category_summaries": category_summaries,
        "alignment_summaries": alignment_summaries,
    }
