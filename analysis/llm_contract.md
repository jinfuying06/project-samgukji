# LLM Interpretation Contract

## Purpose

Convert validated analysis results into grounded, user-appropriate explanations. The model does not calculate new statistics or inspect raw records.

## Allowed inputs

- `analysis/outputs/result.json`
- selected rows from `research/evidence_matrix.csv`
- user context explicitly approved in product requirements

## Required output

Output must satisfy `analysis/schemas/interpretation.schema.json`.

Each claim must include:

- `claim_id`
- type: `observation`, `interpretation`, or `recommendation`
- plain-language text
- one or more `evidence_refs`
- uncertainty/limitations
- risk level

## Refusal / abstention

Return `status: insufficient_evidence` when:

- a requested conclusion has no result/evidence ID
- required data is missing or stale
- the population does not match
- the request asks for a prohibited high-risk conclusion
- cited values conflict

## Prohibited behavior

- inventing numbers, sources, diagnoses, causes, or certainty
- exposing raw sensitive records
- silently changing units or denominators
- turning group-level association into individual prediction

## Versioning

- Provider/model: `[TBD]`
- Prompt version: `[TBD]`
- Parameters: `[TBD]`
- Safety policy version: `[TBD]`
- Eval set version: `[TBD]`

