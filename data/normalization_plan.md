# Normalization Plan

Status: `DRAFT — execution requires B0 approval`

## Non-destructive contract

- Raw bytes and paths remain unchanged.
- All transforms write to the private analysis zone.
- Every output records input checksum, pipeline version, parameters, and timestamp.

## Planned steps

1. Decode with recorded source encoding.
2. Preserve original Unicode text.
3. Create optional normalized Unicode derivative.
4. Create optional simplified/traditional mapping as a separate field.
5. Remove crawler/HTML artifacts with logged rules.
6. Segment work/volume/chapter/paragraph without discarding original locators.
7. Assign source, evidence, entity, and event candidate IDs.
8. Validate counts, hashes, round-trip locators, and source-layer separation.

## Decisions required before execution

- `[TBD: edition mapping]`
- `[TBD: script conversion policy]`
- `[TBD: annotation separation]`
- `[TBD: permitted excerpt storage]`
- `[TBD: first sample scope]`

