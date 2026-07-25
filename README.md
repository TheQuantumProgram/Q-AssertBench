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
python -m pip install -e .
```

### 3. Validate the benchmark tasks

```bash
python -m qasserbench.cli.validate_tasks
```

### 4. Generate assertion candidates

```bash
export QAB_API_KEY="your-api-key"
python -m qasserbench.cli.run_generation \
  outputs/generated_instances/quickstart/model-a/generation_records.jsonl \
  --client openai-compatible \
  --api-base-url https://your-provider.example/v1 \
  --model your-provider/model-a \
  --task-id QAB01 \
  --task-id QAB02 \
  --trials 2
```

### 5. Evaluate generated results

```bash
python -m qasserbench.cli.run_evaluation \
  path/to/generation_records.jsonl \
  path/to/trial_results.jsonl
```

### 6. Summarize trial-level results

```bash
python -m qasserbench.cli.summarize_results \
  path/to/trial_results.jsonl \
  path/to/summary.json
```

### 7. Batch-evaluate a run directory

```bash
find outputs/generated_instances/YOUR_RUN -name generation_records.jsonl | while read -r gen; do
  model_dir=$(dirname "$gen")
  rel=${model_dir#outputs/generated_instances/}
  mkdir -p "outputs/raw_results/$rel" "outputs/summaries/$rel"

  python -m qasserbench.cli.run_evaluation \
    "$gen" \
    "outputs/raw_results/$rel/trial_results.jsonl"

  python -m qasserbench.cli.summarize_results \
    "outputs/raw_results/$rel/trial_results.jsonl" \
    "outputs/summaries/$rel/summary.json"
done
```

## Client Notes

- you must supply your own key through an environment variable such as `QAB_API_KEY`
- different providers may require different base URLs, model IDs, token limits, timeouts, or even a different client mode such as `anthropic-native` or `gemini-native`
- manifest-driven generation is available through `python -m qasserbench.cli.run_generation --manifest path/to/manifest.yaml`

The evaluation pipeline is provider-agnostic once a `generation_records.jsonl` file has been produced. This scoring stage converts generated assertions into execution outcomes, alignment scores, and aggregate summaries.

## Project Structure

- `Benchmark_Tasks/`: canonical task catalog, including prompts, gold assertions, and fault-injected counterparts
- `src/qasserbench/`: benchmark loader, generation clients, execution runtime, evaluation logic, and reporting utilities
- `python -m qasserbench.cli.run_generation`: repeated assertion generation for single-model or manifest-driven runs
- `python -m qasserbench.cli.run_evaluation`: execution-based evaluation from `generation_records.jsonl` to `trial_results.jsonl`
- `python -m qasserbench.cli.summarize_results`: summary aggregation from trial-level results
- `python -m qasserbench.cli.validate_tasks`: structural validation for the task catalog
