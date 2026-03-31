"""Thin wrapper around run_evaluation for summary generation."""

from __future__ import annotations

import argparse

from qasserbench.reporting.aggregate import aggregate_trial_results
from qasserbench.reporting.io import read_trial_results, write_summary


def summarize(input_path: str, output_path: str, pass_k_values: tuple[int, ...] = (1, 5)) -> None:
    records = read_trial_results(input_path)
    summary = aggregate_trial_results(records, pass_k_values=pass_k_values)
    write_summary(summary, output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize evaluated trial results.")
    parser.add_argument("input", help="Path to trial_results.jsonl")
    parser.add_argument("output", help="Path to summary JSON")
    parser.add_argument("--pass-k", nargs="*", type=int, default=[1, 5], help="Pass@k values to compute")
    args = parser.parse_args()

    summarize(args.input, args.output, pass_k_values=tuple(args.pass_k))
    raise SystemExit(0)
