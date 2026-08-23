# Git Rules

Version: 0.1.0

## Purpose

This document defines how changes must be organized, reviewed, and committed.

The objective is to produce a clean, understandable Git history where every commit represents a single logical change and can be reviewed or reverted independently.

---

# Terminology

The keywords **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are interpreted as described in RFC 2119.

---

# Commit Principles

## GIT-001

**Title**

Atomic Commits

**Priority**

MUST

**Rule**

Each commit MUST represent one logical change.

A commit must have a single purpose.

**Rationale**

Atomic commits simplify code reviews, debugging, cherry-picking, and rollbacks.

**Verification**

The commit message can be summarized in one sentence describing one responsibility.

---

## GIT-002

**Title**

Do Not Mix Concerns

**Priority**

MUST

**Rule**

Do not combine unrelated changes in the same commit.

Examples include:

- Feature + Refactor
- Backend + Frontend
- Bug Fix + Formatting
- Documentation + New Functionality

**Rationale**

Mixed commits are difficult to review and difficult to revert.

**Verification**

Removing the commit should remove exactly one logical change.

---

## GIT-003

**Title**

Incremental Development

**Priority**

MUST

**Rule**

Large tasks must be divided into smaller implementation steps.

Each completed step should produce a coherent state of the project.

**Rationale**

Incremental development reduces risk and improves reviewability.

**Verification**

The task can be divided into multiple reviewable commits.

---

## GIT-004

**Title**

Keep the Repository Working

**Priority**

MUST

**Rule**

Each proposed commit should leave the project in a working state.

Avoid creating commits that intentionally break builds or tests.

**Rationale**

Every commit should be a stable checkpoint.

**Verification**

The project builds successfully and existing tests continue to pass.

---

# Agent Behavior

## GIT-010

**Title**

Suggest Commit Messages

**Priority**

MUST

**Rule**

Never create commits automatically.

Always propose a commit message and wait for user approval.

**Rationale**

The user remains responsible for repository history.

**Verification**

No commit is created without explicit approval.

---

## GIT-011

**Title**

Describe the Commit

**Priority**

SHOULD

**Rule**

Before proposing a commit, summarize:

- What changed
- Why it changed
- Any important implementation decisions

**Rationale**

A commit should be understandable without reading the entire diff.

**Verification**

A short change summary accompanies the proposed commit.

---

# Commit Scope

## GIT-020

**Title**

Separate Backend and Frontend Changes

**Priority**

SHOULD

**Rule**

When practical, backend and frontend work should be implemented and committed independently.

**Rationale**

Independent commits improve reviewability and simplify rollbacks.

**Verification**

Backend and frontend changes are committed separately whenever they are logically independent.

---

## GIT-021

**Title**

Separate Refactoring from Functional Changes

**Priority**

MUST

**Rule**

Refactoring commits must not introduce behavioral changes.

Functional changes must not include unrelated refactoring.

**Rationale**

Separating refactoring makes reviews significantly easier.

**Verification**

The purpose of the commit is either refactoring or behavior change, but not both.

---

## GIT-022

**Title**

Keep Commits Small

**Priority**

SHOULD

**Rule**

Prefer multiple small commits over one large commit whenever possible.

**Rationale**

Small commits are easier to review and less risky.

**Verification**

Large commits are justified only when the task cannot be reasonably divided.

---
## GIT-023

**Title**

Functional Cohesion

**Priority**

MUST

**Rule**

Each commit MUST implement a single functional capability or engineering objective.

A commit should answer exactly one question:

> What was added or changed?

Good examples:

- Add OCR processing pipeline
- Create Telegram bot integration
- Configure Docker environment
- Add payment confirmation endpoint

Poor examples:

- Core setup
- Initial implementation
- Miscellaneous changes
- Project updates

Avoid grouping unrelated configuration, infrastructure, business logic, and application features into the same commit.

**Rationale**

Functionally cohesive commits are easier to understand, review, test, and revert.

**Verification**

The commit title clearly describes one functional capability or engineering objective.

---

## GIT-024

**Title**

Conventional Commit Messages

**Priority**

MUST

**Rule**

Every proposed commit message MUST follow the Conventional Commits specification.

Supported commit types include:

- feat
- fix
- refactor
- docs
- test
- chore
- perf
- build
- ci

The general format is:

```
<type>(<scope>): <short description>
```

The description MUST:

- Be written in English.
- Use the imperative mood.
- Start with a lowercase letter.
- Avoid ending with a period.
- Clearly describe the functional change.

Examples:

```text
feat(api): add payment confirmation endpoint

feat(ocr): implement image preprocessing pipeline

fix(parser): handle empty OCR responses

refactor(database): simplify session management

docs(readme): document Docker setup

test(api): add integration tests for payment routes

build(docker): add development environment
```

**Rationale**

Conventional Commit messages create a consistent repository history, improve readability, and enable automation for changelogs, releases, and versioning.

**Verification**

Every proposed commit message follows the Conventional Commits format and accurately describes a single functional change.