---
name: project-discovery
description: Conducts a structured discovery interview with the user to create PROJECT_SPEC.md. Use ONLY when PROJECT_SPEC.md is missing, incomplete, outdated, or when starting a new project or major feature area. Do NOT use for regular implementation tasks once PROJECT_SPEC.md exists.
---

# Project Discovery Skill

Version: 0.1.0

## Purpose

This skill guides the AI agent through a structured discovery process with the user to create a comprehensive `PROJECT_SPEC.md` before any implementation begins. The goal is to achieve shared understanding between the user and the AI agent.

---

# When to Use

**Execute this skill when:**
- `PROJECT_SPEC.md` does not exist in the project root
- `PROJECT_SPEC.md` exists but is incomplete, outdated, or inconsistent
- Starting work on a new project or major feature area

**Do NOT execute when:**
- `PROJECT_SPEC.md` exists and is current
- The task is a small bug fix or trivial change within well-understood scope

---

# Discovery Process

## Phase 1: Project Identity

Ask **one question at a time**, wait for answer, then proceed.

1. **Project Name**: What should this project be called?
2. **Problem Statement**: What problem does this project solve? Why does it need to exist?
3. **Target Users**: Who will use this system? (internal team, external customers, other services)
4. **Success Criteria**: How will we know this project is successful? (specific, measurable outcomes)

## Phase 2: Scope & Boundaries

5. **Core Objectives**: List 3-5 main objectives this project must achieve.
6. **Non-Objectives (Out of Scope)**: What does this project explicitly NOT do? This prevents scope creep.
7. **Stakeholders**: Who else is affected? (other teams, upstream/downstream systems, compliance)

## Phase 3: Technical Context

8. **Technology Stack** (Mandatory vs Preferred):
   - Language(s) & version(s) required
   - Framework(s) required
   - Database(s) required
   - Infrastructure requirements (Docker, Kubernetes, serverless, etc.)
   - Any forbidden technologies

9. **Architecture Style**: What architectural pattern? (REST API, GraphQL, event-driven, microservices, monolith, CLI, library)
10. **Integration Points**: External systems, APIs, services this project must connect to.

## Phase 4: Constraints & Decisions

11. **Hard Constraints**: Non-negotiable requirements (regulatory, performance, budget, timeline, team skills)
12. **Engineering Decisions** (preliminary): Any decisions already made? (e.g., "Repository pattern", "Async endpoints", "JWT auth", "Event sourcing")
13. **Performance Requirements**: Latency, throughput, scalability targets.
14. **Security Requirements**: Auth requirements, data sensitivity, compliance needs.

## Phase 5: Current State

15. **Existing Code**: Is there existing code to work with? If yes, describe structure.
16. **Current Status**: What's done, in progress, planned?
17. **Known Risks/Blockers**: Technical debt, dependencies, unknowns.

---

# Execution Rules

## RULE-DISCOVERY-001: One Question at a Time

**Priority**: MUST

Ask exactly ONE question, wait for the user's response, then ask the next. Never batch questions.

## RULE-DISCOVERY-002: Provide Recommendations

**Priority**: SHOULD

For each question, provide your recommended answer based on context. Let the user confirm or override.

## RULE-DISCOVERY-003: Resolve Dependencies Between Decisions

**Priority**: MUST

If a later question depends on an earlier answer, note the dependency and revisit if the earlier answer changes.

## RULE-DISCOVERY-004: No Assumptions

**Priority**: MUST

If the user's answer is ambiguous, ask for clarification. Never assume.

## RULE-DISCOVERY-005: Confirm Before Writing

**Priority**: MUST

After all questions are answered, present the complete PROJECT_SPEC.md draft for user review. Wait for explicit approval before writing the file.

---

# Output

Upon completion, create/update `PROJECT_SPEC.md` in the project root using the template at `.ai/specifications/PROJECT_SPEC.template.md`.

The generated spec becomes the **single source of truth** for all subsequent work. All agents must read it before planning or implementing.

---

# Agent Instructions

When invoked, the agent should:

1. Check if `PROJECT_SPEC.md` exists in project root
2. If not (or if incomplete), announce: "I'll run the Project Discovery skill to create PROJECT_SPEC.md"
3. Proceed through Phase 1-5 questions sequentially
4. Present final draft for approval
5. Write `PROJECT_SPEC.md` on approval
6. Continue with the engineering workflow