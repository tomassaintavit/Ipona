# AI Engineering Standard (Claude Code)

This project follows the **AI Engineering Standard** defined in `AGENTS.md`.

## Instructions for Claude Code

Read and follow `AGENTS.md` for all engineering tasks. It contains:

- Project initialization workflow (PROJECT_SPEC.md creation via Project Discovery skill)
- Mandatory reading order (PROJECT_SPEC.md → AI_RULES.md → ENGINEERING_PROCESS.md → DEFINITION_OF_DONE.md → SKILLS_INDEX.md)
- Conditional standards loading (Git, Testing, Dependencies, Security, Documentation)
- General agent behavior rules

## Quick Reference

| Task | Read |
|------|------|
| Any task | `AGENTS.md` + `PROJECT_SPEC.md` |
| Git commits | `.ai/standards/GIT_RULES.md` |
| Testing | `.ai/standards/TESTING_RULES.md` |
| Dependencies | `.ai/standards/DEPENDENCY_RULES.md` |
| Security | `.ai/standards/SECURITY_RULES.md` |
| Documentation | `.ai/standards/DOCUMENTATION_RULES.md` |

## Workflow

Follow `.ai/processes/ENGINEERING_PROCESS.md` for the complete engineering workflow.

## Project Discovery

If `PROJECT_SPEC.md` does not exist, execute the Project Discovery skill (`.ai/skills/project-discovery/SKILL.md`) to create it through structured questioning.

---

*This file exists for Claude Code compatibility. The canonical configuration is `AGENTS.md`.*