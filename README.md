# AI Engineering Standard

A modular engineering framework for AI-assisted software development. Ensures AI agents (opencode, Claude Code, Cursor, etc.) work with consistent practices, explicit planning, incremental changes, and verifiable results.

**Version**: 0.1.0

---

## Quick Start

### 1. Create a Project from the Template

```bash
# Option A: GitHub template (recommended)
gh repo create my-project --template tomassaintavit/ai-engineering-standard --public
cd my-project

# Option B: Direct clone
git clone https://github.com/tomassaintavit/ai-engineering-standard my-project
cd my-project
rm -rf .git && git init  # Fresh history
```

### 2. Restart Your AI Agent

opencode reads its configuration (including `skills.paths`) once at startup, not per session. After cloning, **quit and restart opencode** so it registers the skills from `.ai/skills/`.

### 3. Run Project Discovery

Your new project has no `PROJECT_SPEC.md` yet — by design. When you open opencode in the project:

- The **`project-discovery`** skill auto-invokes (its description fires when `PROJECT_SPEC.md` is missing).
- It runs a structured interview (**17 questions**) and creates `PROJECT_SPEC.md` from `.ai/specifications/PROJECT_SPEC.template.md`.
- If it doesn't auto-fire, invoke it explicitly: *"run the project-discovery skill"*.

Once `PROJECT_SPEC.md` exists, the skill stays dormant.

### 4. Start Working

```bash
# Load context and verify setup
./bootstrap.sh

# Your AI agent reads AGENTS.md automatically
# Follow the engineering process: bootstrap → understand → plan → implement → validate → commit
```

---

## How It Works

### For the AI Agent

1. **Reads `AGENTS.md`** — Entry point with mandatory reading order
2. **Runs `./bootstrap.sh`** — Loads context, verifies `PROJECT_SPEC.md` exists
3. **Uses runtime skills** — `opencode.json` registers `.ai/skills/` via `skills.paths`; the `project-discovery` skill auto-invokes when no spec exists
4. **Follows `ENGINEERING_PROCESS.md`** — 10-phase workflow with exit criteria
5. **Loads conditional standards** — Only when task requires them
6. **Commits via pre-commit hook** — Enforces Conventional Commits

### For You (Human)

- **`PROJECT_SPEC.md`** — Static project contract (what & why)
- **`PROJECT_STATUS.md`** — Live project dashboard (features, decisions, debt, risks)
- **`bootstrap.sh --all`** — Load all standards for review
- **`.ai/templates/`** — ADR, Threat Model, Migration Guide templates
- **Pre-commit hook** — Blocks non-conventional commit messages

---

## Repository Structure

```
.ai/
├── standards/           # 6 engineering standards
│   ├── AI_RULES.md          # Core principles (simplicity, scope, decisions)
│   ├── GIT_RULES.md         # Atomic commits, Conventional Commits
│   ├── TESTING_RULES.md     # Pyramid, organization, coverage, property-based
│   ├── DEPENDENCY_RULES.md  # Pinning, SCA, licensing, supply chain
│   ├── SECURITY_RULES.md    # Auth, headers, rate limiting, threat modeling
│   └── DOCUMENTATION_RULES.md # Diátaxis, C4, changelog, executable examples
├── processes/
│   └── ENGINEERING_PROCESS.md  # Unified 10-phase workflow
├── checklists/
│   └── DEFINITION_OF_DONE.md   # Completion criteria
├── specifications/
│   ├── PROJECT_SPEC.template.md   # Static contract template
│   └── PROJECT_STATUS.md          # Live project dashboard
├── skills/
│   ├── SKILLS_INDEX.md         # Skill catalog
│   └── project-discovery/
│       └── SKILL.md            # 17-question discovery interview
└── templates/
    ├── ADR.template.md
    ├── THREAT_MODEL.template.md
    └── MIGRATION_GUIDE.template.md

Root files:
├── AGENTS.md              # Canonical agent config (all agents)
├── CLAUDE.md              # Claude Code entry point
├── opencode.json          # opencode config
├── bootstrap.sh           # Context loader
├── MANIFEST.md            # Architecture index
├── VERSION                # 0.1.0

scaffold/ (starter files to copy into a new project root):
├── AGENTS.md.template
├── CLAUDE.md.template
└── opencode.json.template
```

---

## Scaffold & Templates

### `scaffold/` — Starters for projects that don't come from the template

If you created your project via the GitHub template or clone, the root files (`AGENTS.md`, `CLAUDE.md`, `opencode.json`) are already there — skip this section.

Use `scaffold/` when adopting the standard in an **existing project** that has no AI configuration yet:

```bash
cd existing-project
cp ../ai-engineering-standard/scaffold/AGENTS.md.template ./AGENTS.md
cp ../ai-engineering-standard/scaffold/CLAUDE.md.template ./CLAUDE.md
cp ../ai-engineering-standard/scaffold/opencode.json.template ./opencode.json
cp -r ../ai-engineering-standard/.ai ./
cp ../ai-engineering-standard/bootstrap.sh ./
```

Then restart your agent and run Project Discovery (Quick Start, step 3).

### `.ai/templates/` — Document templates for during development

These are not startup files. They are used while building the project:

- `ADR.template.md` — Architecture Decision Records
- `THREAT_MODEL.template.md` — Security threat modeling
- `MIGRATION_GUIDE.template.md` — Breaking-change migrations

Referenced by the standards in `.ai/standards/`; used only when those situations arise.

---

## Key Commands

```bash
# Load mandatory context only
./bootstrap.sh

# Load with specific standards
./bootstrap.sh --git --test --security

# Load everything
./bootstrap.sh --all

# Verify all document versions match the VERSION file
./bootstrap.sh --check-version

# Invoke the project-discovery skill manually (inside opencode)
# Ask: "run the project-discovery skill"

# Verify commit message format
git commit -m "feat(api): add user endpoint"  # ✅ passes
git commit -m "added user endpoint"           # ❌ blocked
```

---

## Standards Overview

| Standard | When to Load | Key Rules |
|----------|--------------|-----------|
| **AI_RULES** | Always | Simplicity, scope, explicit decisions, no assumptions |
| **GIT_RULES** | Commits | Atomic, conventional commits, no mixed concerns |
| **TESTING_RULES** | New/modified code | Pyramid, fakes > mocks, coverage ≥80%, property-based |
| **DEPENDENCY_RULES** | Deps changes | Pin versions, SCA, license allowlist, supply chain |
| **SECURITY_RULES** | Auth/secrets/data | Headers, rate limiting, threat modeling, SAST/SCA |
| **DOCUMENTATION_RULES** | API/arch changes | Diátaxis, C4 diagrams, changelog, executable examples |

---

## Agent Compatibility

| Agent | Config File | Status |
|-------|-------------|--------|
| **opencode** | `opencode.json` | ✅ Native |
| **Claude Code** | `CLAUDE.md` | ✅ Native |
| **Cursor** | `AGENTS.md` | ✅ Reads automatically |
| **Codex** | `AGENTS.md` | ✅ Reads automatically |
| **Custom** | `AGENTS.md` | ✅ Universal |

---

## Customization

1. **Add skills**: Create `.ai/skills/<name>/SKILL.md` + register in `SKILLS_INDEX.md`
2. **Modify standards**: Edit files in `.ai/standards/`
3. **Add templates**: Place in `.ai/templates/` + reference in standards
4. **Project config**: Fill `PROJECT_SPEC.md` via Project Discovery

---

## Philosophy

> **Agent behavior depends on the standard, not conversation memory.**

Every document has a single responsibility. Standards define rules, processes define execution order, specifications define context, checklists define completion, skills define implementation knowledge.

---

## License

MIT — Use freely in your projects.