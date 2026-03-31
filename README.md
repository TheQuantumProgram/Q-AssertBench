# Q-AssertBench Project Code

This directory contains the runnable benchmark framework and structured task catalog for Q-AssertBench.

## Canonical Layout

- `benchmark_data/tasks/`: canonical benchmark task catalog (`qab01` to `qab31`)
- `src/qasserbench/`: shared loaders, generation helpers, execution engine, evaluation, and reporting
- `scripts/run_generation.py`: collect repeated raw generation records
- `scripts/run_evaluation.py`: evaluate raw generations into trial-level results
- `scripts/summarize_results.py`: aggregate evaluated trial results into summaries
- `scripts/validate_tasks.py`: validate all task manifests
- `experiment_data/`: generated records, trial results, and summaries

## Working Convention

Use the local environment in `.venv/` when running scripts or tests.

Examples:

```bash
PYTHONPATH=src ./.venv/bin/python scripts/validate_tasks.py
PYTHONPATH=src ./.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v
```

## Generation Clients

The generation pipeline supports:

- `static`: deterministic local smoke testing
- `openai-compatible`: any endpoint compatible with the OpenAI Python SDK chat-completions API

Example:

```bash
export QAB_API_KEY=...
export QAB_API_BASE_URL=https://your-provider.example/v1
export QAB_MODEL=your-model-name

PYTHONPATH=src ./.venv/bin/python scripts/run_generation.py experiment_data/generated/run.jsonl \
  --client openai-compatible \
  --task-id QAB01 \
  --trials 2
```

## Legacy Source Material

The old imported task layout is archived under `archive/Q-AssertBench(old)/`.
It is kept only as migration source material and is no longer part of the canonical runtime layout.
