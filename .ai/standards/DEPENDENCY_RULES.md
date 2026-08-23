# Dependency Rules

Version: 0.1.0

## Purpose

This document defines the mandatory dependency management rules that every AI agent must follow when working on this repository.

---

# Terminology

The keywords **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are interpreted as described in RFC 2119.

---

# Dependency Principles

## DEP-001: Minimize Dependencies

**Priority**: MUST

**Rule**: Prefer standard library over external dependencies. Add dependencies only when they provide significant value.

**Rationale**: Each dependency adds maintenance burden, security surface, and supply-chain risk.

**Verification**: New dependency justified in implementation plan with alternatives considered.

---

## DEP-002: Pin Versions

**Priority**: MUST

**Rule**: All dependencies MUST be pinned to exact versions (no ranges, no floating versions).

**Rationale**: Reproducible builds require exact versions.

**Verification**: Lock files present and committed; no version ranges in manifests.

---

## DEP-003: Audit Before Adding

**Priority**: MUST

**Rule**: Before adding a dependency, verify: active maintenance, license compatibility, no known vulnerabilities, reasonable popularity.

**Rationale**: Abandoned or vulnerable dependencies create technical debt and risk.

**Verification**: Dependency audit documented in PR or commit message.

---

## DEP-004: Separate Dev and Runtime Dependencies

**Priority**: MUST

**Rule**: Development dependencies (linters, test frameworks, build tools) MUST be separated from runtime dependencies.

**Rationale**: Production deployments should not include dev tools.

**Verification**: Clear separation in package manager configuration.

---

## DEP-005: No Transitive Dependency Reliance

**Priority**: SHOULD

**Rule**: Do not rely on transitive dependencies. If your code imports it, declare it directly.

**Rationale**: Transitive dependencies can change without notice.

**Verification**: All imports have corresponding direct dependencies.

---

# Automated Scanning & Updates

## DEP-010: Automated Dependency Updates

**Priority**: MUST

**Rule**: Configure automated dependency update bots:
- Enable Dependabot (GitHub), Renovate (GitLab/GitHub), or similar
- Group updates: security (immediate), patch (weekly), minor (bi-weekly), major (monthly with review)
- Auto-merge for patch/security if CI passes; require review for minor/major
- Include changelog links in PR descriptions

**Rationale**: Automated updates prevent large, risky upgrade batches and reduce zero-day exposure.

**Verification**: Bot configured; PRs created on schedule; auto-merge working for safe updates.

---

## DEP-011: Vulnerability Scanning (SCA)

**Priority**: MUST

**Rule**: Scan dependencies for known vulnerabilities on every PR and scheduled daily:
- Use osv-scanner, Trivy, or GitHub Dependabot alerts
- Fail build on CVSS ≥ 7.0 (high/critical) with fix available
- Track findings without fix: document compensating controls, target remediation date
- Generate SBOM (Software Bill of Materials) in CycloneDX or SPDX format on each release

**Recommended Tools**: osv-scanner, Trivy, GitHub Dependabot, Snyk, Grype.

**Verification**: SCA job in CI pipeline; scheduled daily scan; SBOM artifact published with releases.

---

## DEP-012: License Compliance

**Priority**: MUST

**Rule**: 
- Define allowlist of approved licenses (e.g., MIT, Apache-2.0, BSD-2/3-Clause, ISC, MPL-2.0)
- Block dependencies with copyleft licenses (GPL-2.0, GPL-3.0, AGPL, SSPL) in production code
- Allow LGPL only with dynamic linking; document exception
- Run license check in CI; fail on unapproved licenses
- Review new dependency licenses before merge

**Recommended Tools**: `license-checker` (Node), `pip-licenses` (Python), `go-licenses` (Go), `cargo-lichking` (Rust), FOSSA, ScanCode Toolkit.

**Verification**: License scan in CI; zero unapproved licenses in production dependency tree.

---

# Supply Chain Security

## DEP-020: Supply Chain Integrity

**Priority**: SHOULD

**Rule**: 
- Verify package signatures/provenance where available (sigstore/cosign, npm attestations, PyPI trusted publishing)
- Enable artifact attestations in CI (GitHub: `actions/attest-build-provenance`)
- Pin package registry URLs; avoid unofficial mirrors
- Use `npm audit signatures` / `pip verify` / `go mod verify` to validate integrity
- Reject packages without provenance in high-security contexts

**Recommended Tools**: sigstore/cosign, SLSA framework, GitHub Artifact Attestations, `npm audit signatures`, `pip index versions`.

**Verification**: Provenance verification in CI; SBOM includes provenance data; unsigned packages flagged.

---

## DEP-021: Dependency Confusion Prevention

**Priority**: SHOULD

**Rule**: 
- Use scoped packages for private registries (`@org/package`) — prevents public registry fallback
- Configure registry priority: private first, then public
- Set `publishConfig.registry` in package.json; use `.npmrc`/`pip.conf` with tokens (not passwords)
- Monitor for typosquatting (similar names on public registry)
- Claim organization scope on public registries even if private-only

**Rationale**: Dependency confusion attacks inject malicious code via public registry packages matching private names.

**Verification**: Scoped packages used; registry config audited; no public packages matching private scopes.

---

# Monorepo & Workspace Strategy

## DEP-030: Monorepo Dependency Management

**Priority**: SHOULD

**Rule**: For monorepos:
- Use native workspaces: npm/yarn/pnpm workspaces, Cargo workspaces, Go modules, Python `uv`/`poetry` monorepo
- Share lockfile at root; single version policy for shared deps (avoid diamond dependencies)
- Internal packages: version independently (changesets) or lockstep (single version)
- Build tool: Turbo, Nx, or native (pnpm `--filter`, `cargo build --workspace`)
- CI: affected-only builds (Turbo/Nx) or full matrix

**Rationale**: Monorepos amplify dependency issues; consistent tooling prevents version drift.

**Verification**: Workspace config valid; single lockfile; internal deps resolve correctly; CI builds affected projects.

---

## DEP-031: Peer Dependencies Handling

**Priority**: SHOULD

**Rule**: For libraries/frameworks exposing peer dependencies:
- Declare `peerDependencies` with version ranges (not exact)
- Use `peerDependenciesMeta.optional: true` for truly optional peers
- Document required peer versions in README
- Test against minimum and maximum supported peer versions in CI
- Never bundle peer dependencies in library output

**Rationale**: Incorrect peer dependency handling causes version conflicts for consumers.

**Verification**: Peer deps declared correctly; CI matrix tests min/max peer versions; bundle analysis shows no bundled peers.

---

# Updates

## DEP-040: Regular Updates

**Priority**: SHOULD

**Rule**: Schedule regular dependency updates (monthly for security, quarterly for features).

**Rationale**: Prevents large, risky upgrade batches.

**Verification**: Update schedule documented; automated alerts configured.

---

## DEP-041: Security Updates Immediately

**Priority**: MUST

**Rule**: Apply security patches within 48 hours of advisory publication.

**Rationale**: Known vulnerabilities are actively exploited.

**Verification**: Security update process documented and followed.

---

# Agent Behavior

## DEP-050: Propose Dependency Changes

**Priority**: MUST

**Rule**: Never add/update/remove dependencies silently. Present the change, justification, and impact before implementation.

**Rationale**: Dependency changes affect the entire project.

**Verification**: Dependency changes reviewed and approved before implementation.

---

## DEP-051: Document Rationale

**Priority**: SHOULD

**Rule**: Document why each non-trivial dependency was chosen over alternatives.

**Rationale**: Future maintainers need context for dependency decisions.

**Verification**: Rationale in README, ADR, or dependency manifest comments.

---

# Anti-Patterns (What NOT To Do)

| Anti-Pattern | Why It's Dangerous | Correct Approach |
|--------------|-------------------|------------------|
| Version ranges (`^1.0.0`, `~2.0.0`, `latest`) in lockfile | Non-reproducible builds; surprise breaking changes | Exact versions in lockfile; ranges only in manifest (DEP-002) |
| Committing `node_modules`, `vendor/`, `.venv/` to git | Bloats repo; bypasses supply chain checks; platform-specific | Lockfile only; CI installs from lockfile |
| Ignoring "low/medium" CVEs without triage | Chained exploits; compliance failures; technical debt | Triage all; document acceptance with compensating controls (DEP-011) |
| Using unscoped private packages (`my-lib` vs `@org/my-lib`) | Dependency confusion attack vector | Scoped packages + registry priority (DEP-021) |
| No automated update bot | Manual updates lag; zero-day exposure | Dependabot/Renovate configured (DEP-010) |
| Bundling peer dependencies in library output | Version conflicts for consumers; bundle bloat | Peer deps external; test matrix (DEP-031) |
| Multiple lockfiles in monorepo | Version drift; diamond dependencies | Single root lockfile; workspace protocol (DEP-030) |
| Adding dependencies without audit | Supply chain risk; license violations; bloat | Audit checklist: maintenance, license, vulns, popularity (DEP-003) |

---

# Recommended Tools by Category

| Category | Tools (Language-Agnostic) |
|----------|---------------------------|
| Automated Updates | Dependabot (GitHub), Renovate (GitLab/GitHub/Bitbucket), `pip-tools`/`uv` (Python), `cargo-upgrades` (Rust) |
| Vulnerability Scanning (SCA) | osv-scanner, Trivy, Grype, GitHub Dependabot, Snyk, GitLab Dependency Scanning |
| License Compliance | `license-checker` (Node), `pip-licenses` (Python), `go-licenses` (Go), `cargo-lichking` (Rust), FOSSA, ScanCode Toolkit |
| Supply Chain / Provenance | sigstore/cosign, SLSA GitHub Generator, GitHub Artifact Attestations, `npm audit signatures`, `pip verify`, `go mod verify` |
| Dependency Confusion | Scoped packages (`@org/`), `.npmrc`/`pip.conf` token auth, `pnpm` strict peer resolution |
| Monorepo Management | pnpm workspaces, yarn workspaces, npm workspaces, Cargo workspaces, Go modules, `uv`/`poetry` monorepo, Turbo, Nx |
| Lockfile Management | `pnpm` (fast, strict), `uv` (Python, fast), `npm ci`/`yarn install --frozen-lockfile`, `cargo` (built-in) |
| SBOM Generation | `syft` (Anchore), `cyclonedx-cli`, `spdx-tools`, GitHub Dependency Graph export |
| Peer Dependency Validation | `pnpm` (strict by default), `npm ls`, `yarn why`, `pnpm why` |