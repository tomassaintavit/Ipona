# Security Rules

Version: 0.1.0

## Purpose

This document defines the mandatory security rules that every AI agent must follow when working on this repository.

---

# Terminology

The keywords **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are interpreted as described in RFC 2119.

---

# Secrets Management

## SEC-001: No Secrets in Code

**Priority**: MUST

**Rule**: NEVER commit secrets (API keys, passwords, tokens, private keys) to version control.

**Rationale**: Exposed secrets compromise systems and data.

**Verification**: Pre-commit hooks scan for secrets; secret scanning in CI.

---

## SEC-002: Use Environment Variables

**Priority**: MUST

**Rule**: All secrets MUST be loaded from environment variables or secret managers at runtime.

**Rationale**: Keeps secrets out of codebase and enables rotation.

**Verification**: No hardcoded secrets in source files.

---

## SEC-003: Secret Rotation

**Priority**: SHOULD

**Rule**: Implement secret rotation capability for all production secrets.

**Rationale**: Limits blast radius of compromised credentials.

**Verification**: Rotation procedure documented and tested.

---

# Input Validation

## SEC-010: Validate All Inputs

**Priority**: MUST

**Rule**: Validate and sanitize ALL external inputs (HTTP params, headers, body, file uploads, CLI args).

**Rationale**: Unvalidated input is the primary attack vector.

**Verification**: Validation at system boundaries; no raw input in business logic.

---

## SEC-011: Use Allowlists

**Priority**: SHOULD

**Rule**: Prefer allowlist validation over blocklist for input filtering.

**Rationale**: Allowlists are more secure; blocklists miss novel attacks.

**Verification**: Validation logic uses explicit allowed patterns.

---

## SEC-012: Limit Input Size

**Priority**: MUST

**Rule**: Enforce maximum size limits on all inputs (request body, uploads, parameters).

**Rationale**: Prevents DoS via resource exhaustion.

**Verification**: Size limits configured at entry points (web server, framework, API gateway).

---

# Authentication & Authorization

## SEC-020: Use Established Auth Libraries

**Priority**: MUST

**Rule**: Never implement custom authentication/authorization. Use battle-tested libraries.

**Rationale**: Auth is complex; custom implementations have subtle vulnerabilities.

**Verification**: Auth handled by recognized framework/library (e.g., OAuth2, OIDC, JWT libraries).

---

## SEC-021: Principle of Least Privilege

**Priority**: MUST

**Rule**: Grant minimum permissions necessary. Default deny.

**Rationale**: Limits damage from compromised accounts.

**Verification**: Roles/permissions audited regularly; no wildcard permissions.

---

## SEC-022: Secure Session Management

**Priority**: MUST

**Rule**: Use secure, httpOnly, sameSite cookies for sessions. Implement idle timeout and absolute timeout.

**Rationale**: Prevents session hijacking and fixation.

**Verification**: Session config reviewed; security headers present.

---

# Cryptography

## SEC-030: Use Standard Crypto

**Priority**: MUST

**Rule**: Never implement custom cryptography. Use platform/framework TLS, established libraries for encryption/hashing.

**Rationale**: Custom crypto is almost always broken.

**Verification**: No custom encryption, hashing, or signing implementations.

---

## SEC-031: Password Hashing

**Priority**: MUST

**Rule**: Use argon2, bcrypt, or scrypt with appropriate work factors. Never use MD5, SHA1, SHA256 for passwords.

**Rationale**: Fast hashes enable brute force.

**Verification**: Password storage uses approved algorithm with cost factor >=12.

---

# Security Headers

## SEC-040: Implement Security Headers

**Priority**: MUST

**Rule**: Configure security headers on all HTTP responses:
- Content-Security-Policy (CSP): restrict sources for scripts, styles, frames, etc.
- Strict-Transport-Security (HSTS): enforce HTTPS with max-age >= 31536000; includeSubDomains; preload
- X-Frame-Options: DENY or SAMEORIGIN
- X-Content-Type-Options: nosniff
- Referrer-Policy: strict-origin-when-cross-origin or stricter
- Permissions-Policy: restrict browser features (camera, microphone, geolocation, etc.)
- Cross-Origin-Opener-Policy: same-origin
- Cross-Origin-Resource-Policy: same-origin

**Rationale**: Browser-enforced headers provide defense-in-depth against XSS, clickjacking, MIME sniffing, and data leakage.

**Verification**: Security headers present on all responses; CSP report-only mode used during development; `securityheaders.com` or `observatory.mozilla.org` score A+.

---

## SEC-041: Content Security Policy (CSP) Management

**Priority**: SHOULD

**Rule**: 
- Start with restrictive CSP; use `report-only` mode to collect violations before enforcing
- Allow `inline` scripts/styles only via nonces or hashes; avoid `unsafe-inline`
- Define explicit `script-src`, `style-src`, `img-src`, `font-src`, `connect-src`, `frame-src`
- Use `base-uri 'self'` and `form-action 'self'`
- Document CSP exceptions with justification

**Rationale**: CSP is the most effective defense against XSS but requires iterative tuning.

**Verification**: CSP header enforced (not report-only) in production; zero violations in CSP reports for 30 days.

---

# Rate Limiting & Abuse Prevention

## SEC-050: Implement Rate Limiting

**Priority**: MUST

**Rule**: Apply rate limiting at multiple layers:
- Edge/CDN: global IP-based limits (e.g., 1000 req/min)
- Application: per-user limits on auth endpoints (login: 5/min, register: 3/hour)
- API: per-client limits with token buckets (e.g., 100 req/min burst 200)
- Database: connection pool limits; query timeouts

**Rationale**: Prevents brute force, credential stuffing, API abuse, and DoS.

**Verification**: Rate limits enforced; 429 responses with `Retry-After` header; metrics on limit hits.

---

## SEC-051: Account Protection

**Priority**: SHOULD

**Rule**: 
- Implement progressive delays on failed login (exponential backoff)
- Lock accounts after N failures (e.g., 5) with time-based or admin unlock
- Notify users of suspicious login activity (new device, location, IP)
- Implement breach detection (check credentials against known breaches via HaveIBeenPwned API)

**Rationale**: Reduces credential stuffing and account takeover success rates.

**Verification**: Lockout mechanism tested; notifications sent; breach checks in registration/password change.

---

# Security Logging & Monitoring

## SEC-060: Structured Security Logging

**Priority**: MUST

**Rule**: Log security-relevant events in structured JSON format:
- Authentication: login success/failure, logout, MFA events, password changes
- Authorization: permission changes, role assignments, access denied
- Data access: sensitive data reads, exports, bulk operations
- Configuration: security setting changes, header modifications
- Errors: validation failures, rate limit hits, CSP violations

Fields: timestamp, event_type, user_id, ip, user_agent, outcome, risk_level, correlation_id.

**Rationale**: Enables SIEM ingestion, alerting, and forensic investigation.

**Verification**: Logs structured; sampled in development, complete in production; retention >= 1 year.

---

## SEC-061: Alerting on Security Events

**Priority**: SHOULD

**Rule**: Configure real-time alerts for:
- Multiple failed logins from same IP/user (brute force)
- Privilege escalation attempts
- CSP violation spikes
- Rate limit exhaustion
- New admin user creation
- Secret rotation failures

**Rationale**: Reduces mean-time-to-detect for active attacks.

**Verification**: Alert rules defined; tested monthly; runbook documented.

---

# File Upload Security

## SEC-070: Secure File Uploads

**Priority**: MUST

**Rule**: 
- Validate MIME type via magic bytes (not extension or Content-Type header)
- Maintain allowlist of permitted types (e.g., image/png, application/pdf)
- Scan uploads with antivirus (ClamAV) or cloud scanning (VirusTotal, AWS GuardDuty)
- Generate random filenames; store outside webroot or in private object storage (S3/GCS with signed URLs)
- Enforce size limits per type (SEC-012)
- Serve downloads via signed URLs with expiration; set `Content-Disposition: attachment`

**Rationale**: Prevents RCE via malicious uploads, polyglot files, and path traversal.

**Verification**: Upload rejection tests for disallowed types; AV scan integration verified; no direct file access via URL.

---

# CORS Configuration

## SEC-080: Restrictive CORS Policy

**Priority**: MUST

**Rule**: 
- Define explicit `Access-Control-Allow-Origin` (no `*` with credentials)
- Allow only required methods (`GET, POST, PUT, DELETE` typically)
- Allow only required headers (`Content-Type, Authorization` typically)
- Set `Access-Control-Allow-Credentials: true` only when cookies/auth required
- Set `Access-Control-Max-Age` for preflight caching (e.g., 86400)
- Reject requests from unlisted origins with 403

**Rationale**: Prevents cross-origin data theft and CSRF via misconfigured CORS.

**Verification**: CORS headers match allowlist; preflight requests handled correctly; no wildcard with credentials.

---

# Security Testing in CI

## SEC-090: Static Application Security Testing (SAST)

**Priority**: MUST

**Rule**: Run SAST on every PR:
- Use semantic grep rules (semgrep) for language-agnostic patterns
- Include OWASP Top 10 rule sets
- Fail build on high/critical findings
- Suppress false positives with documented justification

**Recommended Tools**: semgrep (primary), CodeQL (GitHub), SonarQube.

**Verification**: SAST job in CI pipeline; zero high/critical findings on main branch.

---

## SEC-091: Software Composition Analysis (SCA)

**Priority**: MUST

**Rule**: Scan dependencies for known vulnerabilities on every PR and scheduled daily:
- Use osv-scanner, Trivy, or GitHub Dependabot alerts
- Fail on CVSS >= 7.0 (high/critical) with fix available
- Track and triage findings without fix (document compensating controls)

**Recommended Tools**: osv-scanner, Trivy, GitHub Dependabot, Snyk.

**Verification**: SCA job in CI; scheduled daily scan; SBOM generated (CycloneDX/SPDX).

---

## SEC-092: Secret Scanning

**Priority**: MUST

**Rule**: Scan for secrets in code, history, and artifacts on every push:
- Pre-commit hook (trufflehog, gitleaks) for developers
- CI scan for full history
- Revoke and rotate any detected secrets immediately

**Recommended Tools**: trufflehog, gitleaks, GitHub Secret Scanning.

**Verification**: Zero secrets in main branch history; pre-commit hook installed.

---

# Threat Modeling

## SEC-100: Lightweight Threat Modeling

**Priority**: SHOULD

**Rule**: For new features or architecture changes, document a threat model using STRIDE:
1. **S**poofing: Can attacker impersonate user/service?
2. **T**ampering: Can data be modified in transit/storage?
3. **R**epudiation: Can actions be denied without proof?
4. **I**nformation Disclosure: Can sensitive data leak?
5. **D**enial of Service: Can service be made unavailable?
6. **E**levation of Privilege: Can attacker gain higher permissions?

Document: threats identified, mitigations implemented, residual risk accepted.

**Template**: `.ai/templates/THREAT_MODEL.template.md`

**Rationale**: Proactive threat identification reduces reactive firefighting.

**Verification**: Threat model document exists for new features; reviewed by peer; residual risks tracked.

---

# Agent Behavior

## SEC-110: Security Review for Auth Changes

**Priority**: MUST

**Rule**: Any change to authentication, authorization, or secret handling requires explicit security review.

**Rationale**: Auth changes are high-risk.

**Verification**: Security review documented in PR/commit.

---

## SEC-111: Report Vulnerabilities Responsibly

**Priority**: MUST

**Rule**: If you discover a security issue, report it privately. Do not disclose publicly until fixed.

**Rationale**: Responsible disclosure protects users.

**Verification**: Vulnerability reporting process documented.

---

# Anti-Patterns (What NOT To Do)

| Anti-Pattern | Why It's Dangerous | Correct Approach |
|--------------|-------------------|------------------|
| Rolling your own auth/crypto | Subtle vulnerabilities; no peer review | Use established libraries (SEC-020, SEC-030) |
| Logging secrets, PII, or tokens | Log aggregation exposes sensitive data | Redact sensitive fields; use structured logging (SEC-060) |
| CORS `*` with credentials | Allows any site to make authenticated requests | Explicit origin allowlist (SEC-080) |
| Rate limiting only in frontend | Trivially bypassed | Multi-layer rate limiting (SEC-050) |
| Storing uploads in webroot with original names | Direct execution/path traversal | Random names, private storage, signed URLs (SEC-070) |
| Ignoring "low" severity CVEs | Chained exploits; compliance failures | Triage all; document acceptance (SEC-091) |
| CSP with `unsafe-inline` | Defeats XSS protection | Nonces/hashes for inline content (SEC-041) |
| No threat modeling for new features | Unknown attack surface | STRIDE lightweight model (SEC-100) |

---

# Recommended Tools by Category

| Category | Tools (Language-Agnostic) |
|----------|---------------------------|
| SAST | semgrep, CodeQL, SonarQube |
| SCA / Vulnerability Scanning | osv-scanner, Trivy, Dependabot, Snyk |
| Secret Scanning | trufflehog, gitleaks, GitHub Secret Scanning |
| Antivirus / File Scanning | ClamAV, VirusTotal API, AWS GuardDuty, GCP Container Analysis |
| CSP / Security Headers Testing | securityheaders.com, observatory.mozilla.org, csp-evaluator.withgoogle.com |
| Rate Limiting | Redis (token bucket), Arcjet, Cloudflare, Kong, Envoy |
| Structured Logging | structlog (Python), pino (Node), zap (Go), serilog (.NET) |
| Threat Modeling | Microsoft Threat Modeling Tool, OWASP Threat Dragon, draw.io |
| Breach Detection | HaveIBeenPwned API (k-anonymity) |