# Migration Guide Template

Use this template for breaking changes (major versions). Copy to `docs/migrations/vX-to-vY.md` (e.g., `v1-to-v2.md`).

---

# Migration Guide: v[X] → v[Y]

**Version**: v[Y].0.0
**Release Date**: YYYY-MM-DD
**Previous Version**: v[X].Z.Z
**Status**: Draft | Published

---

## Overview

Brief summary of what changed and why.

- **Breaking Changes**: N
- **New Features**: N
- **Deprecations**: N
- **Estimated Migration Effort**: Low / Medium / High

---

## Why This Change?

Explain the rationale for breaking changes:
- Technical debt being addressed
- Architectural improvement
- Performance/scaling requirement
- Security enhancement
- Alignment with industry standards

---

## Breaking Changes

### 1. [Change Title]

**Impact**: High / Medium / Low
**Affected**: [API endpoints, config options, CLI commands, database schema, etc.]

#### Before (v[X])
```language
// Code/config example showing old way
```

#### After (v[Y])
```language
// Code/config example showing new way
```

#### Migration Steps
1. Step 1
2. Step 2
3. Step 3

#### Automated Migration
- [ ] Codemod/script available: `command --migrate`
- [ ] Manual only

---

### 2. [Change Title]

**Impact**: High / Medium / Low
**Affected**: [...]

#### Before (v[X])
```language
// Old way
```

#### After (v[Y])
```language
// New way
```

#### Migration Steps
1. Step 1
2. Step 2

---

## Deprecations (Non-Breaking)

| Feature | Deprecated In | Removal Target | Replacement |
|---------|---------------|----------------|-------------|
| Old API endpoint | v[X].Y | v[Y+1].0 | New endpoint |
| Config option `foo` | v[X].Y | v[Y+1].0 | `bar` |

---

## New Features (Optional Migration)

| Feature | Description | Opt-in Required? |
|---------|-------------|------------------|
| New caching layer | Improved performance | No (automatic) |
| Enhanced auth | Better security | Yes (config flag) |

---

## Step-by-Step Migration Checklist

### Pre-Migration
- [ ] Backup database / export data
- [ ] Review all breaking changes above
- [ ] Run test suite on current version (baseline)
- [ ] Notify stakeholders / schedule maintenance window

### Migration
- [ ] Update dependency to v[Y].0.0
- [ ] Run automated migration script (if available)
- [ ] Apply manual config changes
- [ ] Update application code for breaking changes
- [ ] Run database migrations
- [ ] Update CI/CD pipelines if needed

### Post-Migration
- [ ] Run full test suite
- [ ] Run integration tests against staging
- [ ] Monitor error rates / performance metrics
- [ ] Verify critical user journeys
- [ ] Update documentation references
- [ ] Remove deprecated code/config (after grace period)

---

## Rollback Procedure

If critical issues arise:

1. **Immediate**: Revert deployment to v[X].Z.Z
2. **Database**: Restore from pre-migration backup
3. **Config**: Revert config changes
4. **Communicate**: Notify team/stakeholders of rollback

**Rollback Time Target**: < 30 minutes

---

## Testing Strategy

- [ ] Unit tests updated for new APIs
- [ ] Integration tests cover migration path
- [ ] E2E tests verify critical paths
- [ ] Load testing on migrated system
- [ ] Chaos testing (if applicable)

---

## Support

- **Migration Questions**: [Slack channel / email / issue tracker]
- **Known Issues**: [Link to tracking issue]
- **Office Hours**: [Date/time for live support]

---

## Changelog Reference

See [CHANGELOG.md](../CHANGELOG.md#vY00---YYYY-MM-DD) for complete change list.