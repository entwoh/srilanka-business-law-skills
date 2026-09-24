# CLAUDE.md

Project rules for Claude Code sessions in this repository.

- This repo is an open-source set of Claude Skills on Sri Lankan business law.
- We are refactoring to a graph-ready architecture described in
  [docs/optimization-plan.md](docs/optimization-plan.md). Read it before any structural change.
  The node/edge model is defined in [ontology/ontology.md](ontology/ontology.md).
- **NEVER change the legal meaning of content during refactors.** Moving, splitting,
  re-heading and adding metadata are allowed. If content looks wrong or outdated, do not edit
  it — add an entry to [REVIEW-TODO.md](REVIEW-TODO.md) (file, line, issue).
- Node IDs are permanent. Never rename or reuse an ID; use `SUPERSEDES`.
- Generated files (`graph/*`, `references/_map.md`, `dist/*`) are never edited by hand;
  regenerate with scripts.
- Python scripts must be stdlib-only (Python 3.9+), no network access.
- Keep SKILL.md bodies ≤150 lines and descriptions ≤1024 characters.
- After any content change run:
  `python scripts/validate.py && python scripts/build_graph.py --check`
  (until those scripts exist — Phase 4 — run `python scripts/validate_frontmatter.py`).
