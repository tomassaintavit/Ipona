# AI Engineering Standard

Version: 0.1.0

## Purpose

The AI Engineering Standard defines a modular engineering framework for AI-assisted software development.

Each document within this standard has a single responsibility and should be referenced only for its intended purpose.

---

# Architecture

The standard is organized into five categories.

## Standards

Standards define engineering constraints and mandatory rules.

- AI_RULES.md
- GIT_RULES.md
- TESTING_RULES.md
- DEPENDENCY_RULES.md
- SECURITY_RULES.md
- DOCUMENTATION_RULES.md

---

## Processes

Processes define how engineering work is performed.

- ENGINEERING_PROCESS.md

---

## Specifications

Specifications define project-specific information.

- PROJECT_SPEC.md — static project contract (goals, stack, constraints). Created by Project Discovery.
- PROJECT_SPEC.template.md — template for PROJECT_SPEC.md.
- PROJECT_STATUS.md — live project dashboard (features, decisions, debt, risks, metrics).

---

## Checklists

Checklists define objective completion criteria.

- DEFINITION_OF_DONE.md

---

## Skills

Skills define reusable implementation procedures for specific technologies or engineering tasks.

Index: SKILLS_INDEX.md

Examples include:

- project-discovery (core)
- fastapi (planned)
- docker (planned)
- postgresql (planned)
- telegram (planned)
- testing (planned)
- authentication (planned)

---

# Scaffold

`scaffold/` contains starter files to copy into the root of a new project:

- AGENTS.md.template
- CLAUDE.md.template
- opencode.json.template

These are copies of the working root files, used as a quick-start for projects bootstrapped from this standard.

---

# Design Principles

Every document MUST have a single responsibility.

Standards define rules.

Processes define execution order.

Specifications define project context.

Checklists define completion criteria.

Skills define implementation knowledge.

---

# Versioning

The standard follows semantic versioning.

- Major versions introduce incompatible changes.
- Minor versions introduce new documents or rules.
- Patch versions introduce clarifications or corrections.

The single source of truth for the current version is the `VERSION` file at the project root.

Every document carries a `Version:` header matching the `VERSION` file so it stays self-contained and readable by agents.

## Releasing a New Version

1. Update the `VERSION` file to the new version.
2. Update the `Version:` header in every document under `.ai/` plus `AGENTS.md` and `MANIFEST.md`.
3. Verify consistency: `./bootstrap.sh --check-version` must report `Version <X> matches all documents`.
4. Commit as a single atomic change (e.g. `chore(release): bump to X.Y.Z`).