# 2026-08-03 - Repository Memory System

## Session Summary

The user requested that this Git repository become the central transferable
project memory so Codex can continue work from any PC after pulling the latest
Git state.

## Requests

- Analyze the whole repository, Git state, current code, and available
  conversation context before changing files.
- Create durable project documentation under `docs/`.
- Add `AGENTS.md` with mandatory start, change, and finish instructions.
- Add PlantUML diagrams based only on the real project.
- Add sync, validation, and Git hook installation scripts for PowerShell and
  Bash.
- Add GitHub Actions, PR template, and issue templates.
- Add safe Git hooks that detect missing documentation updates.
- Do not commit or push yet.

## Decisions

- Keep documentation mostly ASCII/English for reliable cross-platform tooling.
- Preserve Persian product/business meaning in glossary and domain descriptions.
- Validate PlantUML files syntactically by checking required markers; rendering
  requires an external PlantUML runtime.
- Do not add CODEOWNERS until a GitHub owner/reviewer handle is confirmed.

## Changes

- Added repository memory docs, UML sources, scripts, hooks, and GitHub
  templates.

## Result

- Pending validation in the current work item.

## Next Action

- Run documentation validation, Django checks, and Django tests.
