# Q-AssertBench Project Code

Q-AssertBench is a benchmark framework for studying assertion generation in quantum programs. This repository contains the runnable task catalog, generation clients, execution-based evaluation pipeline, and reporting utilities for running new assertion-generation studies.

## Overview

The public artifact is organized around three components:

- benchmark tasks with prompts, gold assertions, and designated faulty counterparts
- generation entry points that query external model APIs with credentials supplied through environment variables
- an execution-based evaluator that scores generated assertions into trial-level and summary-level benchmark results

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/TheQuantumProgram/Q-AssertBench.git
cd Q-AssertBench
```

### 2. Create the environment

This repository targets Python 3.10+. We recommend using a virtual environment such as `venv`. The commands below assume a standard Linux shell; other environments may need minor adjustments to shell syntax or virtual-environment activation.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e . --no-deps --no-build-isolation
```

### 3. Validate the benchmark tasks

```bash
python scripts/validate_tasks.py
```

### 4. Generate assertion candidates

```bash
cp examples/client_templates/openai-compatible.example.yaml /tmp/qab-client.yaml
export QAB_API_KEY="your-api-key"
python scripts/run_generation.py --manifest /tmp/qab-client.yaml
```

### 5. Evaluate generated results

```bash
python scripts/run_evaluation.py \
  path/to/generation_records.jsonl \
  path/to/trial_results.jsonl
```

### 6. Summarize trial-level results

```bash
python scripts/summarize_results.py \
  path/to/trial_results.jsonl \
  path/to/summary.json
```

### 7. Batch-evaluate a run directory

```bash
find outputs/generated_instances/YOUR_RUN -name generation_records.jsonl | while read -r gen; do
  model_dir=$(dirname "$gen")
  rel=${model_dir#outputs/generated_instances/}
  mkdir -p "outputs/raw_results/$rel" "outputs/summaries/$rel"

  python scripts/run_evaluation.py \
    "$gen" \
    "outputs/raw_results/$rel/trial_results.jsonl"

  python scripts/summarize_results.py \
    "outputs/raw_results/$rel/trial_results.jsonl" \
    "outputs/summaries/$rel/summary.json"
done
```

## Client Notes

The reference manifest at `examples/client_templates/openai-compatible.example.yaml` is intentionally provider-safe:

- copy it to a writable location and edit the provider-specific fields before running `run_generation.py`
- you must supply your own key through an environment variable such as `QAB_API_KEY`
- different providers may require different base URLs, model IDs, token limits, timeouts, or even a different client mode such as `anthropic-native` or `gemini-native`

The evaluation pipeline is provider-agnostic once a `generation_records.jsonl` file has been produced. This scoring stage converts generated assertions into execution outcomes, alignment scores, and aggregate summaries.

## Project Structure

- `benchmark_data/tasks/`: canonical task catalog, including prompts, gold assertions, and fault-injected counterparts
- `src/qasserbench/`: benchmark loader, generation clients, execution runtime, evaluation logic, and reporting utilities
- `scripts/run_generation.py`: repeated assertion generation for single-model or manifest-driven runs
- `scripts/run_evaluation.py`: execution-based evaluation from `generation_records.jsonl` to `trial_results.jsonl`
- `scripts/summarize_results.py`: summary aggregation from trial-level results
- `scripts/validate_tasks.py`: structural validation for the task catalog
- `examples/client_templates/`: provider-safe reference manifests for common client configurations
