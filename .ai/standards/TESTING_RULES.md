# Testing Rules

Version: 0.1.0

## Purpose

This document defines the mandatory testing rules that every AI agent must follow when working on this repository.

---

# Terminology

The keywords **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are interpreted as described in RFC 2119.

---

# Test Principles

## TEST-001: Test Pyramid

**Priority**: MUST

**Rule**: Follow the testing pyramid: many unit tests, fewer integration tests, few end-to-end tests.

**Rationale**: Unit tests are fast, isolated, and pinpoint failures. Integration/E2E tests are slower and more brittle.

**Verification**: Unit tests comprise >70% of test suite.

---

## TEST-002: Test New Functionality

**Priority**: MUST

**Rule**: All new functionality MUST include tests.

**Rationale**: Untested code is unreliable code.

**Verification**: New functions/classes have corresponding test files.

---

## TEST-003: Test Behavior, Not Implementation

**Priority**: SHOULD

**Rule**: Tests should verify observable behavior, not internal implementation details.

**Rationale**: Implementation-coupled tests break during refactoring.

**Verification**: Tests remain valid after internal refactoring.

---

## TEST-004: Deterministic Tests

**Priority**: MUST

**Rule**: Tests MUST be deterministic. No flaky tests.

**Rationale**: Non-deterministic tests erode confidence in the test suite.

**Verification**: Running tests multiple times yields identical results.

---

## TEST-005: Fast Test Suite

**Priority**: SHOULD

**Rule**: Unit test suite should complete in <30 seconds.

**Rationale**: Slow tests discourage frequent execution.

**Verification**: CI test stage completes within time budget.

---

# Test Organization

## TEST-010: Test Structure and Naming

**Priority**: MUST

**Rule**: Organize tests by type and mirror source structure:
- `tests/unit/` — unit tests, mirroring `src/` or `lib/` package structure
- `tests/integration/` — integration tests, grouped by subsystem
- `tests/e2e/` — end-to-end tests, grouped by user journey
- Naming: `test_<unit>_<scenario>_<expected>` (e.g., `test_user_login_valid_credentials_returns_token`)
- One test file per source module: `user_service.py` → `tests/unit/test_user_service.py`

**Rationale**: Consistent structure enables discovery, navigation, and selective test runs.

**Verification**: Test directory structure matches source; naming convention followed; `pytest --collect-only` shows organized hierarchy.

---

## TEST-011: Test Doubles Strategy

**Priority**: MUST

**Rule**: Choose test doubles by boundary type:
- **Fakes** (preferred): Working implementations for DB, cache, message queues — use Testcontainers, in-memory SQLite, fakeredis
- **Stubs**: Fixed responses for external HTTP APIs — use MockServiceWorker (MSW), Pact, WireMock
- **Mocks** (last resort): Only for verifying side effects at boundaries (email sent, event published) — use `unittest.mock`, `jest.mock`, `testify/mock`
- **Never mock**: Internal functions, private methods, value objects, domain logic

**Rationale**: Fakes provide confidence; mocks couple to implementation. Over-mocking creates brittle tests that pass but miss bugs.

**Verification**: No mocks for internal code; fakes used for infrastructure; mock call verification only at system boundaries.

---

## TEST-012: Test Data Management

**Priority**: SHOULD

**Rule**: Manage test data with builders/factories, not hardcoded fixtures:
- Use builder pattern: `UserBuilder().with_email("x@y.com").build()`
- Factories for complex object graphs: `OrderFactory.create(with_items=3)`
- Data must be realistic (valid emails, past dates, varied lengths) — not `foo`, `bar`, `test@test.com`
- Each test owns its data; no shared mutable state between tests
- Clean up via transactions (DB) or scoping (DI containers)

**Rationale**: Hardcoded data causes false positives/negatives; builders enable readable, maintainable test setup.

**Verification**: No magic strings in test bodies; builder/factory used for all entities; tests run in parallel without interference.

---

# Coverage & Quality

## TEST-020: Coverage Targets

**Priority**: SHOULD

**Rule**: Enforce minimum coverage thresholds:
- Lines: ≥80%
- Branches: ≥70%
- Functions: ≥90%
- Critical paths (auth, payments, security): 100% branches
- Coverage measured on unit + integration; E2E excluded

**Rationale**: Coverage without branch/function metrics misses critical logic paths.

**Verification**: CI fails if thresholds not met; coverage reports generated per PR.

---

## TEST-021: Mutation Testing

**Priority**: SHOULD

**Rule**: Run mutation testing on critical modules to verify test effectiveness:
- Mutators: conditionals, arithmetic, returns, null checks
- Minimum mutation score: 70% for critical paths
- Run periodically (weekly) or on security-sensitive changes

**Recommended Tools**: `mutmut` (Python), `stryker` (JS/TS), `go-mutesting` (Go).

**Verification**: Mutation score reported; surviving mutants reviewed for test gaps.

---

# Specialized Testing

## TEST-030: Async and Concurrency Testing

**Priority**: SHOULD

**Rule**: 
- Test async code with real event loops; avoid `asyncio.run` in tests
- Verify race conditions: run concurrent operations 100+ times (stress)
- Test timeouts, cancellation, backpressure explicitly
- Use deterministic schedulers where available (e.g., `asyncio.test_utils`)

**Verification**: Concurrency tests detect known race conditions; no flaky async tests.

---

## TEST-031: Database Testing

**Priority**: SHOULD

**Rule**: 
- Use Testcontainers for real DB (PostgreSQL, MySQL, MongoDB) in integration tests
- Run migrations before test suite; seed via factories
- Wrap each test in transaction; rollback after (no cleanup needed)
- Test queries against real schema; verify indexes, constraints, triggers
- For unit tests: use in-memory SQLite only if dialect-compatible; otherwise fake repository

**Recommended Tools**: Testcontainers, `pytest-postgresql`, `sqlalchemy` with transaction rollback.

**Verification**: Integration tests use real DB; schema changes caught; no test pollution.

---

## TEST-032: External Service Testing

**Priority**: SHOULD

**Rule**: 
- Contract testing (Pact) for HTTP/gRPC dependencies: consumer defines expectations, provider verifies
- Mock servers (MSW, WireMock) for unit tests — record/playback real responses
- Test resilience: timeouts, retries, circuit breakers, rate limits, partial failures
- Never test against real external services in CI (unreliable, slow, side effects)

**Recommended Tools**: Pact, MockServiceWorker (MSW), WireMock, Testcontainers for localstack.

**Verification**: Contract tests in CI for each dependency; mock servers match real API behavior.

---

## TEST-033: Property-Based Testing

**Priority**: SHOULD

**Rule**: Apply property-based testing for:
- Pure functions (serialization round-trip, parsing/printing inverse)
- Algorithms (sorting, filtering, aggregation invariants)
- Data validation (boundary conditions, malformed input handling)
- State machines (transition validity, invariant preservation)
- Generate 100+ cases per property; shrink failures to minimal counterexample

**Recommended Tools**: `hypothesis` (Python), `fast-check` (JS/TS), `gopter` (Go), `proptest` (Rust).

**Verification**: Properties documented; CI runs property tests; minimal counterexamples reproducible.

---

# Agent Behavior

## TEST-040: Run Tests Before Commit

**Priority**: MUST

**Rule**: Run the full test suite before proposing a commit.

**Rationale**: Prevents pushing broken code.

**Verification**: All tests pass locally before commit proposal.

---

## TEST-041: Update Tests When Behavior Changes

**Priority**: MUST

**Rule**: When modifying existing behavior, update affected tests.

**Rationale**: Outdated tests give false confidence.

**Verification**: No test failures after behavior change.

---

## TEST-042: Test Edge Cases

**Priority**: SHOULD

**Rule**: Include tests for edge cases: empty inputs, null values, boundaries, error conditions.

**Rationale**: Edge cases are where bugs hide.

**Verification**: Edge case coverage visible in test files.

---

# Anti-Patterns (What NOT To Do)

| Anti-Pattern | Why It's Dangerous | Correct Approach |
|--------------|-------------------|------------------|
| Testing private methods / implementation details | Breaks on refactor; false confidence | Test public behavior only (TEST-003) |
| Mocking internal functions | Couples test to implementation; misses integration bugs | Use fakes for infrastructure; test real code (TEST-011) |
| Shared mutable test state | Flaky tests; order-dependent failures | Each test owns data; transaction rollback (TEST-012) |
| Hardcoded test data (`foo`, `bar`, `test@test.com`) | Misses validation bugs; unrealistic | Builders/factories with realistic data (TEST-012) |
| Coverage as sole quality metric | Incentivizes trivial tests; misses branch logic | Mutation testing + branch coverage (TEST-020, TEST-021) |
| Testing against real external APIs in CI | Slow, flaky, side effects, rate limits | Contract testing + mock servers (TEST-032) |
| No concurrency testing | Misses race conditions, deadlocks | Stress tests + deterministic schedulers (TEST-030) |
| Only happy-path tests | Production failures on error paths | Edge cases + property-based testing (TEST-042, TEST-033) |

---

# Recommended Tools by Category

| Category | Tools (Language-Agnostic) |
|----------|---------------------------|
| Unit Test Framework | pytest (Python), vitest/Jest (JS/TS), testing (Go), cargo test (Rust), JUnit (JVM) |
| Test Organization | pytest, vitest, Jest — native structure support |
| Test Doubles / Mocking | `unittest.mock` (Python), `msw`/`jest.mock` (JS), `testify/mock` (Go), `mockall` (Rust) |
| Fakes / Testcontainers | Testcontainers (multi-lang), `testcontainers-python`, `testcontainers-go`, `testcontainers-node` |
| Test Data / Builders | `factory_boy` (Python), `factory-girl`/`rosie` (JS), `go-faker`/`go-factory` (Go), `factory_bot` (Ruby) |
| Coverage | `coverage.py` (Python), `c8`/`istanbul` (JS), `go test -cover` (Go), `llvm-cov` (Rust) |
| Mutation Testing | `mutmut` (Python), `stryker` (JS/TS), `go-mutesting` (Go), `cargo-mutants` (Rust) |
| Contract Testing | Pact (multi-lang), Spring Cloud Contract (JVM) |
| Mock Servers | MockServiceWorker (MSW), WireMock, Prism, localstack (AWS) |
| Property-Based Testing | `hypothesis` (Python), `fast-check` (JS/TS), `gopter` (Go), `proptest` (Rust), `hedgehog` (Haskell) |
| Async/Concurrency Testing | `pytest-asyncio`, `asyncio.test_utils` (Python), `fake-timers` (JS), `sync` testing (Go) |