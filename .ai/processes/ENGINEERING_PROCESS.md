# Engineering Process

Version: 0.1.0

## Purpose

This document defines the mandatory engineering process that every AI agent must follow when performing work on this repository.

It combines workflow phases with task-level rules into a single linear process.

---

# Process Overview

Every engineering task MUST follow the process below.

```
Receive Request
        │
        ▼
Phase 1: Load Standards
        │
        ▼
Phase 2: Understand Request
        │
        ▼
Phase 3: Clarify Ambiguities
        │
        ▼
Phase 4: Decompose & Plan
        │
        ▼
Phase 5: Get Approval
        │
        ▼
Phase 6: Implement Incrementally
        │
        ▼
Phase 7: Validate
        │
        ▼
Phase 8: Document
        │
        ▼
Phase 9: Propose Commit
        │
        ▼
Phase 10: Definition of Done
```

---

# Phase 1 — Load Standards

## EP-001

**Objective**

Load the engineering standards required for the current task.

**Requirements**

Always load:

- AI_RULES.md
- PROJECT_SPEC.md

Load additional standards only when relevant:

| Standard | Load When | Key Rules to Apply |
|----------|-----------|-------------------|
| GIT_RULES.md | Planning commits, proposing commit messages, reviewing changes | GIT-001 to GIT-024 |
| TESTING_RULES.md | Adding/modifying functionality, creating/updating tests | TEST-001 to TEST-042 |
| SECURITY_RULES.md | Handling auth, secrets, sensitive data, input validation, file uploads | SEC-001 to SEC-111 |
| DEPENDENCY_RULES.md | Adding/updating/removing dependencies, modifying infrastructure | DEP-001 to DEP-051 |
| DOCUMENTATION_RULES.md | Updating APIs, changing architecture, adding user-facing features | DOC-001 to DOC-051 |
| DEFINITION_OF_DONE.md | Every task (completion criteria) | DONE-001 to DONE-040 |

**Exit Criteria**

The agent understands the engineering constraints for this task.

---

# Phase 2 — Understand Request

## EP-002

**Objective**

Fully understand the requested behavior before proposing a solution.

**Requirements**

- Identify the requested outcome.
- Identify constraints (technical, timeline, budget).
- Identify affected components/files.
- Identify success criteria.

**Verification**

The implementation directly addresses the requested behavior without unnecessary assumptions.

**Exit Criteria**

The requested work is fully understood.

---

# Phase 3 — Clarify Ambiguities

## EP-003

**Objective**

Resolve ambiguities before implementation.

**Requirements**

- Ask questions whenever requirements are incomplete or conflicting.
- Do not assume missing requirements.
- Document answers for future reference.

**Verification**

Open questions are resolved before implementation begins.

**Exit Criteria**

No critical ambiguity remains.

---

# Phase 4 — Decompose & Plan

## EP-004

**Objective**

Transform the request into an actionable implementation plan.

**Requirements**

- Break large work into smaller independent tasks (each with clear objective).
- Define completion criteria for each task (objective, verifiable).
- Identify dependencies between tasks.
- Estimate implementation order.
- Present the plan before writing code.
- When multiple paths exist, recommend the next logical step with justification.

**Verification**

- Each task has a clearly defined objective and completion criteria.
- Completion can be verified without subjective judgment.
- Task execution order follows dependency constraints.
- The implementation follows the approved plan.

**Exit Criteria**

Every task has a clear objective, criteria, and sequence.

---

# Phase 5 — Get Approval

## EP-005

**Objective**

Obtain explicit user approval before high-impact work.

**Required For**

- Architecture changes
- Large refactors
- New dependencies (DEP-050)
- Database schema changes
- Breaking changes (DOC-034)
- Security-sensitive changes (SEC-110)

**Exit Criteria**

Approval received or confirmed not required.

---

# Phase 6 — Implement Incrementally

## EP-006

**Objective**

Implement one task at a time, keeping changes small and focused.

**Requirements**

- Complete one task before starting another.
- Keep changes incremental — each step produces a coherent state.
- Follow applicable engineering standards (AI_RULES.md, etc.).
- Modify only files necessary for the current task (AI_RULES RULE-002).
- Preserve existing behavior unless explicitly changing it (AI_RULES RULE-021).
- Prefer simplicity over premature optimization (AI_RULES RULE-005).

**Verification**

- Only one implementation objective is active at any time.
- Current acceptance criteria are satisfied before moving on.
- Every modified file directly supports the requested task.
- Existing functionality continues to behave as before unless intentionally modified.

**Change Summary**

After implementing a task, record a structured change summary to surface assumptions, demonstrate scope discipline, and give reviewers a map of the change:

```
CHANGES MADE:
- <file>: short description of the change

THINGS I DIDN'T TOUCH (intentionally):
- <file>: out of scope or similar gap, left as a separate task

POTENTIAL CONCERNS:
- <concern or open question for the reviewer>
```

The "DIDN'T TOUCH" section shows scope discipline (AI_RULES RULE-002, RULE-020) and surfaces unintended omissions early.

**Exit Criteria**

Current task implemented and validated.

---

# Phase 7 — Validate

## EP-007

**Objective**

Verify the implementation meets acceptance criteria.

**Requirements**

Validation may include:

- Automated tests (unit, integration, e2e) — TEST-010, TEST-040
- Linting / static analysis
- Manual verification
- Build verification

**Rules**

- Run full test suite before proposing commit (TEST-010, TEST-040).
- Update tests when behavior changes (TEST-011, TEST-041).
- Test edge cases: empty inputs, null values, boundaries, errors (TEST-012, TEST-042).
- No flaky tests — tests must be deterministic (TEST-004).
- For security changes: run SAST/SCA/secret scan (SEC-090, SEC-091, SEC-092).
- For dependency changes: run vulnerability scan (DEP-011).

**Evidence Over Assertion**

Validation is non-negotiable. "Seems right" is never sufficient.

- Validation MUST produce observable evidence: test output, build output, lint/typecheck results, exit codes, or runtime data.
- Assertions without evidence (e.g., "tests pass", "it works") MUST be treated as unvalidated.
- Record the evidence (command output or a summary of it) so the result can be verified by review.

**Exit Criteria**

Acceptance criteria satisfied. All tests pass.

---

# Phase 8 — Document

## EP-008

**Objective**

Update project documentation when behavior, architecture, or usage changes.

**Requirements**

Update as needed:

- README
- PROJECT_SPEC.md
- API documentation (OpenAPI, docstrings) — DOC-002
- Architecture Decision Records (ADRs) — DOC-003, DOC-021, template: `.ai/templates/ADR.template.md`
- CHANGELOG (Keep a Changelog format) — DOC-033
- Migration guides for breaking changes — DOC-034, template: `.ai/templates/MIGRATION_GUIDE.template.md`
- Threat models for security-relevant changes — SEC-100, template: `.ai/templates/THREAT_MODEL.template.md`

**Rules**

- Documentation updated in same commit as behavior change (DOC-010, DOC-030).
- Prefer generated docs (from types, OpenAPI) over hand-written (DOC-021, DOC-042).
- Document "why" (rationale, tradeoffs), not just "what" (DOC-004).
- Remove dead documentation for deleted features (DOC-012, DOC-032).
- Organize by Diátaxis: tutorials, how-to, reference, explanation (DOC-010).
- Architecture diagrams as Mermaid in repo (DOC-020).
- Executable examples validated in CI (DOC-041).

**Exit Criteria**

Documentation reflects the current implementation.

---

# Phase 9 — Propose Commit

## EP-009

**Objective**

Prepare the implementation for version control following Git standards.

**Requirements**

Apply GIT_RULES.md:

- Atomic commits — one logical change per commit (GIT-001)
- No mixed concerns (feature + refactor, backend + frontend, etc.) (GIT-002)
- Separate refactoring from functional changes (GIT-021)
- Conventional Commit message format: `type(scope): description` (GIT-024)
- Never create commits automatically — propose and wait for approval (GIT-010)
- Summarize: what changed, why, important decisions (GIT-011)

**Verification**

- Commit message follows Conventional Commits spec (GIT-024)
- Single functional capability per commit (GIT-023)
- Removing the commit removes exactly one logical change (GIT-002)

**Exit Criteria**

Commit proposal ready for user approval.

---

# Phase 10 — Definition of Done

## EP-010

**Objective**

Verify the task is complete against objective criteria.

**Requirements**

Apply DEFINITION_OF_DONE.md:

- Requirements satisfied (matches acceptance criteria) (DONE-001)
- Code quality — follows all applicable standards (DONE-002)
- Validation completed (tests, lint, build, manual) (DONE-003)
- Tests added/updated for new functionality (DONE-010)
- No existing tests broken (DONE-011)
- Documentation updated (DONE-020)
- Git ready (Conventional Commit, atomic) (DONE-030)
- Task summary provided: what changed, why, how validated, remaining limitations (DONE-040)

**Verification**

All completion criteria satisfied without subjective judgment.

**Exit Criteria**

Task complete. Ready for next task or project closure.

---

# Cross-Cutting Rules (Always Apply)

The engineering principles in **AI_RULES.md** (RULE-001 to RULE-021) apply at every phase of this process and take precedence over implementation preferences. Refer to `.ai/standards/AI_RULES.md` as the single authoritative source for these rules.

This process defines the sequence of phases; it does not restate core principles.

---

# Common Rationalizations

AI agents default to the shortest path, which often means skipping phases. When the agent reasons about skipping a step, the rebuttal below MUST apply.

## Skipping the Process

| Rationalization | Reality |
|---|---|
| "This is a small change, I'll skip the process" | Every task, small or large, follows the same process. Skipping phases hides assumptions and creates rework. |
| "I already understand it, no need to clarify" | Ambiguity is only "no ambiguity" after explicit confirmation. Unverified assumptions are the most expensive kind (RULE-012). |
| "I'll document it later" | Documentation written at the end is reconstructed from memory and half of it is missing. Write it with the change (DOC-010). |

## Skipping Validation

| Rationalization | Reality |
|---|---|
| "I'll add tests later" | Tests are the only proof the code works. Without evidence, the change is unvalidated — "seems right" is never sufficient. |
| "The tests take too long to run" | A fast suite is a design goal, not a reason to skip validation. Run the suite before proposing the commit (TEST-010). |
| "It obviously works, I don't need to verify" | Obviousness is not evidence. Validation MUST produce observable output (EP-007). |

## Skipping Git Discipline

| Rationalization | Reality |
|---|---|
| "One giant commit is faster" | A giant commit is impossible to review, debug, or revert. Commit each increment (GIT-001). |
| "The commit message doesn't matter" | Messages are documentation. Future you (and future agents) need to know what changed and why (GIT-011). |
| "I'll fix the scope later" | Unrelated changes make reviews harder and reverts riskier. Split concerns now, not after (GIT-002). |

**Exit Criteria**

No rationalization overrides the applicable process phase or verification requirement.

---

# Agent Instructions

1. **Read this document first** (after PROJECT_SPEC.md and AI_RULES.md)
2. **Follow phases sequentially** — do not skip or reorder
3. **Exit criteria are gates** — do not proceed until satisfied
4. **Document deviations** — if you must skip a phase, explain why
5. **One task at a time** — complete EP-006 for one task before starting another
6. **Bootstrap** — run `./bootstrap.sh [--git|--test|--security|--deps|--docs|--all]` to load context
7. **Skills** — check `.ai/skills/SKILLS_INDEX.md` for applicable skills before starting