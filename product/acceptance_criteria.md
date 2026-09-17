# Acceptance Criteria

## AC-001 `[capability]`

- Given: `[initial state]`
- When: `[user/system action]`
- Then: `[observable outcome]`
- And: `[data/grounding/accessibility condition]`
- Test owner: `[role]`
- Evidence: `[test path]`

## Mandatory negative cases

- Invalid or missing input does not produce a confident result.
- Stale analysis is visibly labeled.
- Unsupported LLM claims are rejected before display.
- User can recover from retryable errors.
- High-risk action requires explicit human confirmation.

