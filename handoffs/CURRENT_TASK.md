# Current Task

- Task ID: `TASK-S0-SETUP`
- Role: `orchestrator`
- Status: `READY`
- Priority: `P0`
- Depends on: `human project owner input`

## Objective

Launch only the S0 concept, private-raw inventory, and research-feasibility tracks; prepare a documented B0 decision without selecting a concept in advance.

## Required inputs

- Existing project scaffold
- User-provided private raw Chinese corpus location
- Product hypotheses and data/privacy constraints

## Allowed write paths

- `PROJECT_BRIEF.md`
- `product/concepts/`
- `data/ingestion_report.md`
- `data/normalization_plan.md`
- `product/problem_definition.md`
- `product/target_user.md`
- `handoffs/OPEN_QUESTIONS.md`
- `handoffs/LAST_HANDOFF.md`
- `handoffs/phase_reports/S0_COMPLETION.md`

## Deliverables

- Three product concepts compared with evidence
- Read-only raw inventory summarized without committing private data
- Research/data feasibility and open rights questions
- S0 completion report and exact B0 approval question

## Acceptance checks

- No raw file is moved, overwritten, normalized, or committed
- No product concept is silently selected
- Material questions are recorded and asked
- B0 report states proposed S1 scope and waits for explicit approval

## Do not do

- Do not implement application code, pixel battles, curriculum, or production UI.
- Do not normalize the raw corpus or run full-corpus analysis.
- Do not proceed to S1 before B0 approval is recorded.
