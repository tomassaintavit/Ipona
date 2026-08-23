# Skills Index

Version: 0.1.0

## Purpose

This document catalogs all available skills for AI agents working in this repository. Skills are reusable implementation procedures for specific technologies or engineering tasks.

Agents should read this index on startup to know what capabilities are available.

---

# Available Skills

## project-discovery (Core)

| Field | Value |
|-------|-------|
| **Path** | `.ai/skills/project-discovery/SKILL.md` |
| **Trigger** | `PROJECT_SPEC.md` missing OR incomplete/outdated |
| **Description** | Structured questioning to create a comprehensive PROJECT_SPEC.md through user interview. Ensures alignment before any implementation. |
| **Inputs** | None (interactive) |
| **Outputs** | `PROJECT_SPEC.md` (created/updated) |
| **When to Use** | Start of any new project or major feature area |
| **Dependencies** | Uses `.ai/specifications/PROJECT_SPEC.template.md` as template |

**Agent Instructions**: When PROJECT_SPEC.md doesn't exist, announce "Running Project Discovery skill" and follow SKILL.md phases sequentially (one question at a time).

**Runtime**: Registered with opencode via `skills.paths` in `opencode.json`. The `description` frontmatter gates auto-invocation: the skill only fires when `PROJECT_SPEC.md` is missing, incomplete, outdated, or at the start of a new project. Once `PROJECT_SPEC.md` exists, the skill stays dormant. Claude Code integration is planned (`.claude/skills/`).

---

## Planned Skills (Not Yet Implemented)

The following skills are planned for future inclusion. Add them by creating `.ai/skills/<name>/SKILL.md`:

| Skill | Domain | Description |
|-------|--------|-------------|
| `fastapi` | Backend | FastAPI project setup, routing, dependency injection, testing |
| `docker` | Infrastructure | Dockerfile, docker-compose, multi-stage builds |
| `postgresql` | Database | Schema design, migrations (Alembic), connection pooling |
| `telegram` | Integration | Bot setup, webhook/polling, command handling |
| `testing` | Quality | Pytest configuration, fixtures, coverage, CI integration |
| `authentication` | Security | JWT, OAuth2, session management, RBAC |
| `redis` | Caching/Queue | Cache patterns, rate limiting, Celery broker |
| `github-actions` | CI/CD | Workflow templates, matrix builds, deployments |

---

# Skill Structure

Each skill MUST follow this structure in its `SKILL.md`:

```markdown
---
name: skill-name
description: What this skill does AND when to trigger it. Use ONLY when <condition>. Do NOT use when <negative condition>.
---

# Skill Name

Version: 0.1.0

## Purpose
What this skill accomplishes.

## When to Use
Trigger conditions (explicit, not vague).

## Prerequisites
Required files, tools, or prior skills.

## Procedure
Step-by-step execution (numbered, one action per step).

## Inputs
Parameters the skill accepts.

## Outputs
Files created/modified.

## Verification
How to confirm success.

## Agent Instructions
How the agent should invoke and execute this skill.
```

Frontmatter requirements:

- `name` — lowercase, hyphen-separated, matches the folder name (e.g. `project-discovery`).
- `description` — what the skill does AND when to trigger it. Front-load trigger keywords. Include "Use ONLY when..." and "Do NOT use..." guards so the skill stays dormant outside its intended scope.

---

# Adding a New Skill

1. Create directory: `.ai/skills/<skill_name>/` (lowercase, hyphen-separated)
2. Create `SKILL.md` following the structure above (frontmatter + body)
3. Add entry to this index (table + planned section)
4. Update AGENTS.md if skill is a core trigger (like project-discovery)
5. Skills under `.ai/skills/` are picked up by opencode automatically via `skills.paths` — no extra registration needed.

---

# Agent Usage

On startup, agent should:

1. Read this index
2. Check trigger conditions for each skill
3. Execute triggered skills before proceeding with task
4. Reference skill procedures when task matches skill domain

Example:
```
Task: "Create FastAPI user endpoint"
→ Check index → fastapi skill exists
→ Read .ai/skills/fastapi/SKILL.md
→ Follow its procedure
```