# Definition of Done

Version: 0.1.0

## Purpose

This document defines the minimum conditions required for a task to be considered complete.

A task MUST NOT be considered finished until all applicable criteria are satisfied.

---

# General Criteria

## DONE-001

Title:
Requirements Satisfied

Priority:
MUST

Requirement:

The implementation satisfies the original task requirements.

Verification:

The completed work can be compared against the acceptance criteria.

---

## DONE-002

Title:
Code Quality

Priority:
MUST

Requirement:

The implementation follows the project's engineering standards.

Verification:

No known violations of applicable standards exist.

---

## DONE-003

Title:
Validation Completed

Priority:
MUST

Requirement:

The implementation has been validated.

Validation may include:

- Automated tests
- Manual verification
- Static analysis
- Build verification

Evidence over assertion is required: the validation MUST produce observable evidence (test output, build output, lint/typecheck results, exit codes, or runtime data). Assertions without evidence (e.g., "it works") are not acceptable.

Verification:

Validation results are documented with evidence that can be verified by review.

---

# Testing Criteria

## DONE-010

Title:
Tests Added or Updated

Priority:
SHOULD

Requirement:

New functionality should include appropriate tests.

Existing tests should be updated when behavior changes.

Verification:

Relevant test coverage exists.

---

## DONE-011

Title:
No Existing Tests Broken

Priority:
MUST

Requirement:

Existing tests must continue passing.

Verification:

The test suite completes successfully.

---

# Documentation Criteria

## DONE-020

Title:
Documentation Updated

Priority:
SHOULD

Requirement:

Documentation must be updated when behavior, architecture, or usage changes.

Verification:

Relevant documentation reflects the current implementation.

---

# Repository Criteria

## DONE-030

Title:
Git Ready

Priority:
MUST

Requirement:

The change is ready according to GIT_RULES.md.

Verification:

A valid commit can be created.

---

# Final Review

## DONE-040

Title:
Task Summary

Priority:
MUST

Requirement:

Provide a summary containing:

- What changed
- Why it changed
- How it was validated
- Any remaining limitations

Verification:

The summary accurately describes the implementation.

---

# Red Flags

The task is NOT complete if any of the following signs are present. These indicate the task is being declared done without meeting the definition of done.

- Tests were not actually run (no test output recorded, only "tests pass" claimed).
- Validation relied on assertion instead of observable evidence (EP-007).
- Unrelated files were modified beyond the requested scope (RULE-002, RULE-020).
- No change summary was recorded after implementation (EP-006).
- Documentation was not updated despite a behavior, architecture, or usage change (DONE-020).
- The commit message does not follow Conventional Commits (GIT-024).
- The change mixes multiple logical concerns in a single commit (GIT-002).
- No task summary was provided (DONE-040).

If any red flag applies, the task must return to the relevant phase before it can be considered complete.