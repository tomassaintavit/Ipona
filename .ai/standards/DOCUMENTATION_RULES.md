# Documentation Rules

Version: 0.1.0

## Purpose

This document defines the mandatory documentation rules that every AI agent must follow when working on this repository.

---

# Terminology

The keywords **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are interpreted as described in RFC 2119.

---

# Documentation Principles

## DOC-001: README Required

**Priority**: MUST

**Rule**: Every project MUST have a README.md with: project description, quick start, development setup, and links to detailed docs.

**Rationale**: README is the entry point for all contributors.

**Verification**: README.md exists and contains required sections.

---

## DOC-002: Document Public APIs

**Priority**: MUST

**Rule**: All public APIs (REST, GraphQL, gRPC, CLI, libraries) MUST have documentation with: endpoints, parameters, responses, errors, examples.

**Rationale**: Undocumented APIs are unusable APIs.

**Verification**: API docs exist and are current (OpenAPI spec, generated docs, or markdown).

---

## DOC-003: Architecture Decision Records (ADRs)

**Priority**: SHOULD

**Rule**: Significant architectural decisions MUST be recorded as ADRs (Architecture Decision Records).

**Rationale**: Captures context for future maintainers.

**Verification**: ADR directory exists; new decisions have ADRs.

**Template**: `.ai/templates/ADR.template.md`

---

## DOC-004: Code Comments for "Why", Not "What"

**Priority**: SHOULD

**Rule**: Comments explain WHY (rationale, constraints, tradeoffs), not WHAT (code is self-documenting for what).

**Rationale**: "What" comments rot; "Why" comments endure.

**Verification**: Comments focus on intent and non-obvious decisions.

---

## DOC-005: Keep Documentation Close to Code

**Priority**: SHOULD

**Rule**: Prefer inline docs (docstrings, type hints, OpenAPI annotations) over separate documentation files.

**Rationale**: Co-located docs stay in sync with code.

**Verification**: Public functions have docstrings; types annotated.

---

# Documentation Framework (Diátaxis)

## DOC-010: Four Documentation Types

**Priority**: SHOULD

**Rule**: Organize documentation into four distinct types (Diátaxis framework):
- **Tutorial** (Learning-oriented): Step-by-step lessons for newcomers; "Let me show you how"
- **How-to Guides** (Problem-oriented): Recipes for specific problems; "How do I...?"
- **Reference** (Information-oriented): Complete, accurate technical descriptions; "What is...?"
- **Explanation** (Understanding-oriented): Context, background, design rationale; "Why is it...?"

**Structure**:
```
docs/
├── tutorials/        # Learning-oriented
├── how-to/           # Problem-oriented
├── reference/        # Information-oriented
│   ├── api/          # API reference (generated from OpenAPI)
│   ├── cli/          # CLI reference
│   └── config/       # Configuration reference
└── explanation/      # Understanding-oriented
    ├── architecture/ # Architecture decisions, diagrams
    └── concepts/     # Domain concepts, design rationale
```

**Rationale**: Different user needs require different documentation structures; mixing types reduces effectiveness.

**Verification**: Documentation organized by type; each type serves its audience; no hybrid pages.

---

## DOC-011: Documentation for Each Type

**Priority**: SHOULD

**Rule**: 
- **Tutorials**: Complete, runnable, testable; no assumptions; lead to working result
- **How-to**: Single task focus; practical; assumes baseline knowledge; flexible paths
- **Reference**: Exhaustive; structured; generated where possible; versioned with API
- **Explanation**: Narrative; connects concepts; not instructional; freely structured

**Verification**: Each doc page identifiable by type; tutorials tested in CI; reference auto-generated.

---

# Architecture Documentation

## DOC-020: Architecture Diagrams (C4 Model)

**Priority**: SHOULD

**Rule**: Document architecture using C4 model levels 1-2:
- **Level 1 (System Context)**: System + users + external systems; one diagram
- **Level 2 (Container)**: Deployable units (apps, databases, queues) + interactions; one diagram
- Optional Level 3 (Component) for complex modules
- Diagrams as code (Mermaid) in repo; rendered in docs
- Update diagrams in same PR as architecture changes

**Template**: Mermaid syntax; stored in `docs/explanation/architecture/`

**Rationale**: Visual architecture enables faster onboarding and better design discussions.

**Verification**: C4 Level 1-2 diagrams exist; Mermaid source in repo; CI renders to verify syntax.

---

## DOC-021: Architecture Decision Records (ADRs) - Detail

**Priority**: SHOULD

**Rule**: Each ADR must include:
- **Title**: Concise, imperative (e.g., "Use PostgreSQL for Primary Data Store")
- **Status**: Proposed | Accepted | Superseded | Deprecated
- **Context**: Problem, constraints, assumptions
- **Decision**: What was chosen, with justification
- **Consequences**: Positive, negative, risks, tradeoffs
- **Alternatives Considered**: What else was evaluated, why rejected
- **Links**: Related ADRs, issues, PRs, external resources

**Naming**: `NNN-short-title.md` (e.g., `001-use-postgresql.md`) in `docs/adr/`

**Rationale**: Structured ADRs enable quick scanning and historical understanding.

**Verification**: ADR directory exists; new decisions have ADRs; template followed.

---

# Maintenance

## DOC-030: Update Docs with Code Changes

**Priority**: MUST

**Rule**: When behavior, API, or architecture changes, update corresponding documentation in the same commit.

**Rationale**: Stale documentation is worse than no documentation.

**Verification**: Doc updates included in PRs that change behavior.

---

## DOC-031: Version Documentation

**Priority**: SHOULD

**Rule**: Documentation should be versioned alongside code (same repo, same version tags).

**Rationale**: Docs for v1.0 should describe v1.0, not main branch.

**Verification**: Release tags include documentation state; versioned doc deployment (e.g., GitHub Pages per tag).

---

## DOC-032: Remove Dead Documentation

**Priority**: SHOULD

**Rule**: Delete documentation for removed features. Do not leave zombie docs.

**Rationale**: Dead docs mislead maintainers.

**Verification**: No documentation references deleted code/features.

---

## DOC-033: Changelog (Keep a Changelog)

**Priority**: SHOULD

**Rule**: Maintain CHANGELOG.md following Keep a Changelog format:
- Sections: Added, Changed, Deprecated, Removed, Fixed, Security
- Entry per change: type, scope, description, PR/link
- "Unreleased" section at top for upcoming changes
- Links to commit/PR for traceability
- Generate from conventional commits where possible

**Template**: `.ai/templates/CHANGELOG.template.md` (or use auto-changelog tools)

**Rationale**: Users and automations expect standardized changelog format.

**Verification**: CHANGELOG.md exists; format validated; entries match commits since last release.

---

## DOC-034: Migration Guides

**Priority**: SHOULD

**Rule**: For breaking changes (major version), provide migration guide:
- What changed (specific APIs, configs, behaviors)
- Why it changed (rationale, benefits)
- Step-by-step migration steps
- Before/after code examples
- Deprecation timeline (if applicable)
- Rollback procedure

**Template**: `.ai/templates/MIGRATION_GUIDE.template.md`

**Rationale**: Reduces upgrade friction; maintains trust.

**Verification**: Migration guide exists for each major version; linked from CHANGELOG and release notes.

---

# Documentation Quality

## DOC-040: Documentation Review Process

**Priority**: SHOULD

**Rule**: 
- Documentation changes require review (same as code)
- Required reviewers for: API docs, architecture docs, tutorials
- Lint documentation in CI: markdownlint (syntax), vale (style/consistency)
- Check for broken links (markdown-link-check)
- Validate examples compile/run (doctest, executable snippets)

**Recommended Tools**: markdownlint, vale, markdown-link-check, doctest.

**Verification**: Doc lint in CI; zero broken links; examples pass CI.

---

## DOC-041: Executable Examples

**Priority**: SHOULD

**Rule**: 
- Code examples in README, tutorials, and reference docs MUST be executable
- Use doctest (Python), `tsx`/`vitest --run` (TypeScript), `go test -run Example` (Go), `cargo test --doc` (Rust)
- Snippets in markdown fenced blocks tagged with language
- CI runs example validation

**Rationale**: Executable examples cannot drift from reality.

**Verification**: Example validation in CI; zero failing examples.

---

## DOC-042: Generated Documentation

**Priority**: SHOULD

**Rule**: Prefer generated documentation over hand-written:
- API reference from OpenAPI spec / gRPC proto / GraphQL schema
- CLI reference from command definitions (Cobra, Click, Clap)
- Config reference from schema (JSON Schema, Pydantic, Zod)
- Database schema from migrations (dbdocs, SchemaSpy)
- TypeDoc / JSDoc / Sphinx / rustdoc for library APIs

**Rationale**: Generated docs cannot drift from implementation.

**Verification**: Generation step in CI; generated artifacts committed or published to doc site.

---

# Agent Behavior

## DOC-050: Propose Documentation Updates

**Priority**: MUST

**Rule**: When implementing changes that affect behavior, propose documentation updates as part of the implementation.

**Rationale**: Documentation is part of the deliverable.

**Verification**: PR includes doc updates or justification for deferral.

---

## DOC-051: Generate, Don't Write (When Possible)

**Priority**: SHOULD

**Rule**: Prefer generated documentation (from types, OpenAPI, tests) over hand-written docs.

**Rationale**: Generated docs cannot drift from implementation.

**Verification**: CI includes doc generation step; generated artifacts committed or published.

---

# Anti-Patterns (What NOT To Do)

| Anti-Pattern | Why It's Dangerous | Correct Approach |
|--------------|-------------------|------------------|
| Documentation only in external wiki (Confluence, Notion) | Not versioned; diverges from code; access barriers | Docs in repo; versioned with code (DOC-031) |
| Comments explaining "what" code does | Redundant; rots quickly; noise | Comments for "why" only (DOC-004) |
| Mixing tutorial/how-to/reference in one page | Confuses readers; serves no audience well | Diátaxis separation (DOC-010) |
| Changelog as raw commit log | Noise; no curation; users can't scan | Keep a Changelog format (DOC-033) |
| No migration guide for breaking changes | Users stuck; lost trust; fork risk | Migration guide per major version (DOC-034) |
| Architecture diagrams in draw.io/Visio only (not in repo) | Not versioned; unrenderable in CI; stale | Mermaid in repo (DOC-020) |
| Hand-written API reference | Drifts from implementation | Generate from OpenAPI/proto (DOC-042) |
| Examples that don't compile/run | False confidence; user frustration | Executable examples in CI (DOC-041) |
| No doc review process | Typos, inconsistencies, missing info | Doc lint + review in CI (DOC-040) |

---

# Recommended Tools by Category

| Category | Tools (Language-Agnostic) |
|----------|---------------------------|
| Doc Site Generators | MkDocs (Python), Docusaurus (JS/TS), Hugo (Go), VitePress (Vue), Sphinx (Python), rustdoc (Rust) |
| Markdown Linting | markdownlint (Node/CLI), vale (style guide), markdown-link-check (broken links) |
| API Doc Generation | OpenAPI Generator, Swagger UI, Redoc, Stoplight Elements, GraphQL Voyager, asyncapi |
| CLI Doc Generation | Cobra (Go), Click (Python), Clap (Rust) — built-in help generation |
| Diagram as Code | Mermaid (primary), PlantUML, Structurizr DSL, C4-PlantUML |
| ADR Tooling | `adr-tools` (bash), `adr-log` (Go), `adr-github` (GitHub), MADR format |
| Changelog Generation | auto-changelog, standard-version, changesets, release-it, semantic-release |
| Example Testing | doctest (Python), `cargo test --doc` (Rust), `go test -run Example` (Go), `tsx`/`vitest` (TS), `pytest --doctest-modules` |
| Doc Review | vale (style), markdownlint (syntax), markdown-link-check (links), reviewdog (CI integration) |
| Versioned Doc Hosting | GitHub Pages, GitLab Pages, Netlify, Vercel, ReadTheDocs, Cloudflare Pages |