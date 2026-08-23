#!/bin/bash
# AI Engineering Standard Bootstrap Script
# Loads mandatory context for AI agents before any task.
# Usage: source bootstrap.sh  OR  ./bootstrap.sh

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AI_DIR="$PROJECT_ROOT/.ai"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_ok() { echo -e "${GREEN}[OK]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_err() { echo -e "${RED}[ERR]${NC} $*"; }

# Check if PROJECT_SPEC.md exists
check_project_spec() {
  if [[ ! -f "$PROJECT_ROOT/PROJECT_SPEC.md" ]]; then
    log_err "PROJECT_SPEC.md not found in project root."
    log_info "Run the Project Discovery skill to create it:"
    log_info "  1. Read .ai/skills/project-discovery/SKILL.md"
    log_info "  2. Answer the discovery questions"
    log_info "  3. Approve the generated PROJECT_SPEC.md"
    return 1
  fi
  log_ok "PROJECT_SPEC.md found"
  return 0
}

# Verify VERSION matches the Version header in every standard/spec document
check_version() {
  local version_file="$PROJECT_ROOT/VERSION"
  if [[ ! -f "$version_file" ]]; then
    log_warn "VERSION file not found at $version_file"
    return 1
  fi
  local current
  current="$(tr -d '[:space:]' < "$version_file")"
  if [[ -z "$current" ]]; then
    log_warn "VERSION file is empty"
    return 1
  fi

  local mismatch=0
  local file version
  while IFS= read -r file; do
    version="$(grep -m1 -E '^Version: ' "$file" | sed 's/^Version: *//' | tr -d '[:space:]' || true)"
    if [[ -n "$version" && "$version" != "$current" ]]; then
      log_err "Version mismatch in $file: '$version' (expected '$current')"
      mismatch=1
    fi
  done < <(find "$AI_DIR" -type f -name '*.md' -print; echo "$PROJECT_ROOT/AGENTS.md"; echo "$PROJECT_ROOT/MANIFEST.md")

  if [[ "$mismatch" -eq 0 ]]; then
    log_ok "Version $current matches all documents"
  else
    log_err "Version check failed: run the release bump to sync all docs"
  fi
  return "$mismatch"
}

# Load a file into context (print to stdout for agent consumption)
load_file() {
  local file="$1"
  local label="$2"
  if [[ -f "$file" ]]; then
    echo "=== $label ==="
    cat "$file"
    echo ""
    return 0
  else
    log_warn "$label not found at $file"
    return 1
  fi
}

# Print usage help
print_help() {
  echo "Usage: ./bootstrap.sh [options]"
  echo ""
  echo "Options:"
  echo "  (no args)    Load mandatory files only"
  echo "  --git        Also load GIT_RULES.md"
  echo "  --test       Also load TESTING_RULES.md"
  echo "  --security   Also load SECURITY_RULES.md"
  echo "  --deps       Also load DEPENDENCY_RULES.md"
  echo "  --docs       Also load DOCUMENTATION_RULES.md"
  echo "  --all        Load all standards"
  echo "  --check-version  Only verify VERSION matches all documents"
  echo "  --help       Show this help"
}

# Main bootstrap flow
main() {
  echo "🚀 AI Engineering Standard Bootstrap"
  echo "====================================="
  echo ""

  # Early handling for standalone flags that don't require PROJECT_SPEC.md
  for arg in "$@"; do
    case "$arg" in
      --check-version)
        check_version
        exit $?
        ;;
      --help|-h)
        print_help
        exit 0
        ;;
    esac
  done

  # 1. Verify PROJECT_SPEC.md
  if ! check_project_spec; then
    exit 1
  fi

  # 2. Load mandatory files
  log_info "Loading mandatory standards..."
  echo ""

  load_file "$PROJECT_ROOT/PROJECT_SPEC.md" "PROJECT_SPEC.md"
  load_file "$AI_DIR/standards/AI_RULES.md" "AI_RULES.md"
  load_file "$AI_DIR/processes/ENGINEERING_PROCESS.md" "ENGINEERING_PROCESS.md"
  load_file "$AI_DIR/checklists/DEFINITION_OF_DONE.md" "DEFINITION_OF_DONE.md"
  load_file "$AI_DIR/skills/SKILLS_INDEX.md" "SKILLS_INDEX.md"

  # 3. Verify version consistency
  check_version || true

  # 4. Optional: Load conditional standards based on args
  for arg in "$@"; do
    case "$arg" in
      --git)
        load_file "$AI_DIR/standards/GIT_RULES.md" "GIT_RULES.md"
        ;;
      --test)
        load_file "$AI_DIR/standards/TESTING_RULES.md" "TESTING_RULES.md"
        ;;
      --security)
        load_file "$AI_DIR/standards/SECURITY_RULES.md" "SECURITY_RULES.md"
        ;;
      --deps)
        load_file "$AI_DIR/standards/DEPENDENCY_RULES.md" "DEPENDENCY_RULES.md"
        ;;
      --docs)
        load_file "$AI_DIR/standards/DOCUMENTATION_RULES.md" "DOCUMENTATION_RULES.md"
        ;;
      --all)
        load_file "$AI_DIR/standards/GIT_RULES.md" "GIT_RULES.md"
        load_file "$AI_DIR/standards/TESTING_RULES.md" "TESTING_RULES.md"
        load_file "$AI_DIR/standards/SECURITY_RULES.md" "SECURITY_RULES.md"
        load_file "$AI_DIR/standards/DEPENDENCY_RULES.md" "DEPENDENCY_RULES.md"
        load_file "$AI_DIR/standards/DOCUMENTATION_RULES.md" "DOCUMENTATION_RULES.md"
        ;;
      *)
        log_warn "Unknown option: $arg (use --help)"
        ;;
    esac
  done

  log_ok "Bootstrap complete. Context loaded."
  echo ""
  echo "Next steps:"
  echo "  1. Read the loaded context above"
  echo "  2. Check SKILLS_INDEX.md for applicable skills"
  echo "  3. Follow ENGINEERING_PROCESS.md Phase 2+"
  echo "  4. For commits, the pre-commit hook enforces Conventional Commits"
}

# If sourced, don't run main (allows loading functions)
# If executed, run main
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi