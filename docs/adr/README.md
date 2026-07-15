# Architecture Decision Records (ADR) Directory

This directory stores formal Architecture Decision Records documenting critical design choices, structural paths, and framework standard selections.

---

## Writing ADRs

All engineers and agents must document significant design deviations using standard ADR templates:

```markdown
# ADR-[NUMBER]: [Title of Decision]

## Status
[Proposed | Approved | Rejected | Deprecated]

## Context
[Describe the problem context and technical constraints]

## Decision
[Details of the architectural decision]

## Consequences
[Describe the consequences, trade-offs, and changes resulting from this choice]
```

## Filename Convention
Name all files consecutively using the pattern `docs/adr/XXXX-short-title.md` (e.g. `0001-python-layout.md`).
