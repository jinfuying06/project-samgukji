# Test Plan

## Layers

| Layer | Focus | Owner |
| --- | --- | --- |
| Schema/unit | entity, evidence, event, result, score arithmetic | Data/Backend |
| Research reliability | coding calibration and adjudication | Research/QA |
| Contract | API ↔ UI and analysis output | Backend/Frontend/QA |
| Integration | source→evidence→score→UI | QA |
| LLM eval | source mode, grounding, abstention | LLM/QA/Eval |
| Accessibility | keyboard, focus, semantics, contrast, chart alternatives | Frontend/QA |
| Rights/publication | only approved text/assets exposed | Research/QA |
| Data boundary | private raw/analysis/curated and runtime DB are untracked; app imports approved export only | Data/Backend/QA |

## Golden cases

- one verified HISTORY_BASE statement
- one ROMANCE-only famous episode queried in history mode
- one disputed annotation
- one alias collision
- one missing-evidence person
- one weight change that reverses rank
- one unsupported “best/strongest” question

## Exit criteria

- All hard-blocker regressions pass
- Critical user journey passes at contract and E2E levels
- Score decomposition sums exactly under defined rounding
- Every displayed claim resolves to available evidence
- No unauthorized excerpt or asset in release bundle
- No private corpus, analytical dataset, curated package, DB, embeddings, or dumps tracked by Git
- Runtime application has no direct raw/analysis workspace dependency
