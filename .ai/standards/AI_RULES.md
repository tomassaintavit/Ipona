# AI Development Constitution

Version: 0.1.0

## Purpose

This document defines the engineering principles and mandatory rules that every AI agent must follow while working on this repository.

Unless explicitly overridden by project-specific documentation, these rules take precedence over implementation preferences.

The objective is to produce software that is simple, maintainable, predictable, and easy to review.

---

# Terminology

The keywords **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are interpreted as described in RFC 2119.

---

# Core Principles

## RULE-001

**Title**

Prefer Simplicity

**Priority**

MUST

**Rule**

Always prefer the simplest solution that satisfies the requirements.

**Rationale**

Simple software is easier to understand, review, test, maintain, and debug.

**Verification**

The proposed solution does not introduce unnecessary abstractions, architectural layers, or dependencies.

---

## RULE-002

**Title**

Minimize Changes

**Priority**

MUST

**Rule**

Modify only the files necessary to complete the requested task.

Avoid unrelated refactoring.

**Rationale**

Small changes reduce review effort and lower the risk of introducing unintended behavior.

**Verification**

Every modified file is directly related to the requested task.

---

## RULE-003

**Title**

Maintain Consistency

**Priority**

MUST

**Rule**

Follow the project's existing architecture, naming conventions, and coding style unless explicitly instructed otherwise.

**Rationale**

Consistency improves maintainability more than personal coding preferences.

**Verification**

The implementation follows the conventions already present in the project.

---

## RULE-004

**Title**

Make Engineering Decisions Explicit

**Priority**

MUST

**Rule**

If multiple reasonable implementations exist, explain the available options, recommend one, and justify the recommendation before implementation.

**Rationale**

Engineering decisions should be transparent and reviewable.

**Verification**

Alternative approaches are presented whenever significant design choices exist.

---

## RULE-005

**Title**

Avoid Premature Optimization

**Priority**

MUST

**Rule**

Do not optimize code unless there is measurable evidence that optimization is necessary.

Prioritize readability over speculative performance improvements.

**Rationale**

Premature optimization increases complexity without guaranteed value.

**Verification**

Performance optimizations are supported by measurable requirements or evidence.

---

# Agent Behavior

## RULE-010

**Title**

Understand Before Implementing

**Priority**

MUST

**Rule**

Analyze the problem before writing code.

Do not begin implementation without understanding the requested behavior.

**Rationale**

Correct understanding prevents incorrect implementations.

**Verification**

The implementation matches the requested behavior without unnecessary assumptions.

---

## RULE-011

**Title**

Explain the Plan

**Priority**

SHOULD

**Rule**

Before implementing medium or large tasks, explain the intended approach.

**Rationale**

A visible implementation plan allows early feedback and avoids unnecessary work.

**Verification**

A concise implementation plan is presented before coding begins.

---

## RULE-012

**Title**

Do Not Assume Requirements

**Priority**

MUST

**Rule**

If requirements are ambiguous or incomplete, ask clarifying questions instead of making assumptions.

**Rationale**

Incorrect assumptions often create unnecessary rework.

**Verification**

Ambiguous requirements are clarified before implementation.

---

# Scope Management

## RULE-020

**Title**

Respect Task Scope

**Priority**

MUST

**Rule**

Complete only the requested work.

Do not introduce unrelated improvements, refactoring, or architectural changes unless explicitly requested.

**Rationale**

Keeping changes focused simplifies reviews and reduces unintended side effects.

**Verification**

Every modification directly supports the requested task.

---

## RULE-021

**Title**

Preserve Existing Behavior

**Priority**

MUST

**Rule**

Avoid changing existing behavior unless the requested task explicitly requires it.

**Rationale**

Unexpected behavioral changes create regressions.

**Verification**

Existing functionality continues to behave as before unless intentionally modified.

---