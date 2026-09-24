# Evals

`queries.jsonl` holds realistic user questions, one JSON object per line. It is used for
LLM-free retrieval scoring (`retrieval_eval.py`, Phase 5) and for skill-trigger tuning
(Phase 11).

| Field | Meaning |
|---|---|
| `id` | Stable `qNNN`. Never renumber. |
| `query` | Written the way a founder, accountant or ops manager actually types it. |
| `type` | `single` · `cross-domain` · `negative` (no `sl-*` skill should trigger) · `singlish` (Sinhala-English mix) |
| `expected_skills` | Skill `name`s from SKILL.md frontmatter that should trigger. Empty for negatives. |
| `expected_topics` | `<skill-folder>/<reference-stem>` (or `shared/<file>`) that should hold the answer. |
| `expected_nodes` | Graph node IDs. Left empty until the owning skill is annotated (Phase 3/7). |
| `notes` | Why the query is in the set: a trap, a playbook candidate, a routing edge case. Never the legal answer. |

Questions only — do not put legal answers in this file.
