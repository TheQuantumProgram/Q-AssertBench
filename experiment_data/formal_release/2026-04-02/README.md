# Formal Experiment Release (2026-04-02)

This directory snapshots the formal experiment artifacts that existed in the workspace on 2026-04-02.

Included generated-instance runs:

- `generated_instances/deepseek-v3.2`
  - status: complete
  - task coverage: `37/37`
  - total records: `740`
- `generated_instances/qwen-3.5-397b-a17b`
  - status: complete
  - task coverage: `37/37`
  - total records: `740`
- `generated_instances/llama-4-scout`
  - status: complete
  - task coverage: `37/37`
  - total records: `740`
- `generated_instances/gpt-5.4`
  - status: complete
  - task coverage: `37/37`
  - total records: `740`
- `generated_instances/claude-sonnet-4-20250514`
  - status: complete
  - task coverage: `37/37`
  - total records: `740`
- `generated_instances/gemini-3.1-flash-lite-preview`
  - status: complete
  - task coverage: `37/37`
  - total records: `740`

Included evaluation artifacts:

- `raw_results/gpt-5.4/trial_results.jsonl`
- `raw_results/claude-sonnet-4-20250514/trial_results.jsonl`
- `raw_results/deepseek-v3.2/trial_results.jsonl`
- `raw_results/gemini-3.1-flash-lite-preview/trial_results.jsonl`
- `raw_results/llama-4-scout/trial_results.jsonl`
- `raw_results/qwen-3.5-397b-a17b/trial_results.jsonl`
- `summaries/gpt-5.4/summary.json`
- `summaries/claude-sonnet-4-20250514/summary.json`
- `summaries/deepseek-v3.2/summary.json`
- `summaries/gemini-3.1-flash-lite-preview/summary.json`
- `summaries/llama-4-scout/summary.json`
- `summaries/qwen-3.5-397b-a17b/summary.json`

Notes:

- This release intentionally excludes smoke tests, token probes, supplementary Gemini runs, and precheck runs.
- Under `generated_instances/`, each uploaded model snapshot keeps only the official `generation_records.jsonl` and `tasks/QAB*.jsonl` files.
- Temporary or recovery-only artifacts such as `_resume_tmp/`, `_corrupt_backup_*/`, `supplements/`, and similar intermediate files are intentionally excluded from this release snapshot.
- The release is organized directly by model under `generated_instances/`, `raw_results/`, and `summaries/`.
