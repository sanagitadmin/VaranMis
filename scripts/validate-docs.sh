#!/usr/bin/env bash
set -euo pipefail

repo="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [ -z "$repo" ]; then
  echo "Not inside a Git repository." >&2
  exit 1
fi
cd "$repo"

required_docs=(
  AGENTS.md README.md docs/README.md docs/PROJECT_OVERVIEW.md
  docs/REQUIREMENTS.md docs/BUSINESS_RULES.md docs/ARCHITECTURE.md
  docs/DATABASE.md docs/API.md docs/SECURITY.md docs/SETUP.md
  docs/DEPLOYMENT.md docs/TESTING.md docs/GIT_WORKFLOW.md
  docs/CHANGELOG.md docs/CURRENT_STATUS.md docs/ROADMAP.md docs/BACKLOG.md
  docs/KNOWN_ISSUES.md docs/DECISION_LOG.md docs/WORK_HISTORY.md
  docs/CONVERSATION_MEMORY.md docs/HANDOFF.md docs/GLOSSARY.md
  docs/history/INDEX.md docs/uml/README.md
)

required_uml=(
  docs/uml/SYSTEM_CONTEXT.puml docs/uml/CONTAINER_DIAGRAM.puml
  docs/uml/COMPONENT_DIAGRAM.puml docs/uml/DEPLOYMENT_DIAGRAM.puml
  docs/uml/DOMAIN_MODEL.puml docs/uml/DATABASE_ERD.puml
  docs/uml/USE_CASES.puml docs/uml/MAIN_SEQUENCES.puml
  docs/uml/STATE_MACHINES.puml docs/uml/ACTIVITY_FLOWS.puml
  docs/uml/AUTHENTICATION_AUTHORIZATION.puml
)

for file in "${required_docs[@]}" "${required_uml[@]}"; do
  [ -f "$file" ] || { echo "Missing required documentation file: $file" >&2; exit 1; }
done

for file in "${required_uml[@]}"; do
  grep -q '@startuml' "$file" || { echo "PlantUML file misses @startuml: $file" >&2; exit 1; }
  grep -q '@enduml' "$file" || { echo "PlantUML file misses @enduml: $file" >&2; exit 1; }
done

echo "Documentation validation passed."
