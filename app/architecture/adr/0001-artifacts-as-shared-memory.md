# ADR 0001: Repository Artifacts as Shared Memory

- Status: Accepted
- Date: `[project start date]`

## Context

Codex and Claude Code do not share reliable chat memory. Research, data, design, implementation, and evaluation must remain auditable across sessions.

## Decision

Approved repository artifacts and handoff files are the canonical project memory. Agents may use chats for interaction but may not require another agent's chat log to continue.

## Consequences

- More explicit schemas, decisions, and handoffs
- Easier cross-model work and audit
- Some documentation overhead
- Simultaneous edits require worktrees and path ownership

