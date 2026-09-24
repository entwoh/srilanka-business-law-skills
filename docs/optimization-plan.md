# Sri Lanka Business Law Skills — Graph-Ready Optimization Plan

Goal: any LLM (Claude first) should find the exact piece of Sri Lankan business-law knowledge it needs **in the fewest tokens and tool calls**, and the same content should be exportable as a **knowledge graph** for Graph-Based Retrieval (GraphRAG, Neo4j, LightRAG, etc.).

How to use this file: it lives at `docs/optimization-plan.md`. Run the phases below in Claude Code **one phase per session** (`/clear` between phases). Each phase has a copy-paste prompt.

---

## 1. Target architecture (what we are building)

### 1.1 Four retrieval layers (progressive disclosure, extended)

| Layer | What | Always loaded? | Target size |
|---|---|---|---|
| L0 | Skill `name` + `description` (10 skills) | Yes, every chat | ≤ 90 words each |
| L1 | `SKILL.md` body = **router** (scope, decision tree, retrieval protocol) | When skill triggers | ≤ 150 lines |
| L2 | `references/_map.md` (generated: node IDs + one-line summary + file:line range) or `kg.py` output | On demand | ≤ 2k tokens |
| L3 | The **exact section** (one node) inside a reference file | On demand, by line range | 100–600 tokens |

Today Claude likely reads whole reference files (L3 = full file). The main saving comes from making L2 cheap and L3 surgical: **read the map → pick node IDs → read only those line ranges.**

### 1.2 Knowledge graph model (single source of truth = Markdown)

Knowledge stays in human-editable Markdown. Every retrievable section becomes a **node** with a stable ID and a small metadata block. A build script compiles the graph. Nobody hand-edits the graph files.

```
Markdown (source) ──build_graph.py──► graph/nodes.jsonl + graph/edges.jsonl
                                     ├─► skills/*/references/_map.md   (LLM-readable index)
                                     ├─► graph/INDEX.md                 (global compact index)
                                     └─► exports: Neo4j CSV / GraphML / Cypher
```

**Node types** (proposal, finalise in Phase 1): `statute`, `provision` (section of a statute), `regulator`, `form`, `obligation`, `deadline`, `procedure`, `concept`, `entity_type` (Pvt Ltd, PLC, sole prop…), `penalty`, `playbook`.

**Edge types**: `CITES`, `ADMINISTERED_BY`, `REQUIRES_FORM`, `HAS_DEADLINE`, `APPLIES_TO`, `TRIGGERS` (event → obligation), `PREREQUISITE_OF`, `DEFINED_IN`, `PENALISED_BY`, `AMENDED_BY`, `SUPERSEDES`, `RELATED`, `STEP_OF` (node → playbook).

**ID convention**: `<prefix>.<topic>.<slug>` — lowercase, dot-separated, never reused, never renamed (use `SUPERSEDES` instead).
Prefixes: `cf` company-formation, `cs` company-secretarial, `sc` shares-and-capital, `cc` commercial-contracts, `emp` employment, `tax`, `fi` foreign-investment, `ip`, `dp` data-protection, `dr` dispute-resolution; shared entities: `statute.`, `reg.`, `form.`, `term.`, `entity.`.

**Section annotation format** (example — IDs and section numbers are illustrative only):

```markdown
## Annual return — filing deadline {#cs.annual-return.deadline}
<!-- kg
type: deadline
cites: [statute.companies-act-2007#sNNN]
administered_by: [reg.roc]
requires_form: [form.roc.annual-return]
applies_to: [entity.pvt-ltd, entity.plc]
related: [tax.filing-calendar.overview]
verified: 2026-09-01
source: <official URL or gazette ref>
-->
**TL;DR:** One or two sentences that answer the most common question directly.

Detail…
```

Why this format: HTML comments don't render on GitHub, cost very few tokens, and keep relations next to the content they describe (easy for contributors). `TL;DR`-first means Claude can often stop reading after 2 lines.

### 1.3 Cross-domain playbooks (pre-computed multi-hop paths)

Real questions cross domains. "Issue shares to a foreign investor" touches shares-and-capital + company-secretarial + foreign-investment (exchange control) + tax. Instead of letting the LLM discover that path every time (expensive), store it once:

```
playbooks/foreign-investor-share-issue.md
  ordered steps → each step = node ID + one-line why
```

This is the same idea as GraphRAG "community summaries": pay the graph-traversal cost once at build time, not at every query.

### 1.4 Retrieval CLI (`kg.py`, stdlib-only Python)

Scripts run without loading their source into context, so a tiny CLI is the cheapest way for Claude to query the graph:

```
python tools/kg.py find "annual return"            # ranked node IDs + 1-line summaries
python tools/kg.py node cs.annual-return.deadline  # summary + file:line range + edges
python tools/kg.py neighbors <id> --hops 1 --type REQUIRES_FORM,HAS_DEADLINE
python tools/kg.py path <idA> <idB>                # shortest relation path
python tools/kg.py playbook foreign-investor-share-issue
python tools/kg.py read <id>                       # prints only that section's text
```

Fallback when code execution is unavailable: SKILL.md tells Claude to read `references/_map.md` and then open the file at the listed lines.

### 1.5 Packaging problem to fix (important)

When a user installs **one** skill folder (claude.ai upload or `~/.claude/skills/`), the repo-level `shared/` folder is **not** available to it. So links from `SKILL.md` to `../../shared/…` break after install. Fix: a build step produces `dist/<skill>/` that is fully self-contained (vendored `kg.py`, the domain's graph slice, and 1-hop "stub" nodes from other domains that say which skill to load).

### 1.6 Target repo layout

```
srilanka-business-law-skills/
├── CLAUDE.md                     # instructions for Claude Code contributors
├── llms.txt                      # entry point for external LLMs/crawlers
├── ontology/
│   ├── ontology.md               # node/edge types, ID rules
│   └── node.schema.json
├── shared/entities/              # statutes, regulators, forms, glossary, entity types (as nodes)
├── skills/<domain>/
│   ├── SKILL.md                  # router, ≤150 lines
│   └── references/
│       ├── _map.md               # GENERATED
│       └── *.md                  # annotated sections
├── playbooks/*.md                # cross-domain paths
├── graph/                        # GENERATED, committed
│   ├── nodes.jsonl
│   ├── edges.jsonl
│   └── INDEX.md
├── tools/kg.py                   # retrieval CLI (stdlib only)
├── scripts/                      # audit, build, validate, export, dist
├── evals/                        # queries + expected nodes
└── dist/                         # GENERATED self-contained skills (release artifact)
```

---

## 2. How to run this in Claude Code

1. `git checkout -b refactor/graph-architecture`
2. Run each phase in a fresh session. Use **Plan mode** (Shift+Tab) first, approve the plan, then let it execute.
3. Review the diff and commit at the end of every phase (`git commit -m "phase N: …"`).
4. **Legal-content safety rule for every phase:** restructuring must not change legal meaning. Anything uncertain goes into `REVIEW-TODO.md`, never silently "fixed".
5. Pilot on one skill (`company-secretarial`) before rolling out to all ten.

---

## 3. Phases (copy-paste prompts)

### Phase 0 — CLAUDE.md, baseline audit, eval set

Create `CLAUDE.md` first (Claude Code reads it every session):

```
Create CLAUDE.md at the repo root with these project rules:

- This repo is an open-source set of Claude Skills on Sri Lankan business law.
- We are refactoring to a graph-ready architecture described in docs/optimization-plan.md. Read it before any structural change.
- NEVER change the legal meaning of content during refactors. Moving, splitting, re-heading and adding metadata are allowed. If content looks wrong or outdated, do not edit it — add an entry to REVIEW-TODO.md (file, line, issue).
- Node IDs are permanent. Never rename or reuse an ID; use SUPERSEDES.
- Generated files (graph/*, references/_map.md, dist/*) are never edited by hand; regenerate with scripts.
- Python scripts must be stdlib-only (Python 3.9+), no network access.
- Keep SKILL.md bodies ≤150 lines and descriptions ≤ 1024 characters.
- After any content change run: python scripts/validate.py && python scripts/build_graph.py --check
```

Then the audit:

```
Phase 0: baseline audit. Do not modify any existing content.

1. Write scripts/audit_tokens.py (stdlib only). For every .md under skills/ and shared/, report: lines, characters, approx tokens (chars/4), number of H2/H3 headings, and outbound links. For each SKILL.md also report description length in chars and words. Output a table to docs/audit-baseline.md, plus totals: always-loaded tokens (all descriptions), per-skill "typical load" (SKILL.md + largest reference).
2. Detect duplication: paragraphs (normalised whitespace) or near-identical sentences appearing in more than one file. List them in the report.
3. Build a cross-reference map: which files link to which, which links are broken, and every reference to ../../shared (these will break after single-skill install — flag them).
4. List every statute, regulator, ROC form, and deadline mentioned anywhere, with file:line, so we can later turn them into canonical entity nodes.
5. Summarise the top 10 token-saving opportunities at the end of the report.
```

```
Phase 0b: create the evaluation set.

Create evals/queries.jsonl with ~50 realistic user questions about Sri Lankan business law. Fields:
{ "id", "query", "type": "single|cross-domain|negative|singlish", "expected_skills": [...], "expected_topics": [...], "notes" }

Mix: 25 single-domain, 15 cross-domain (e.g., foreign investor share issue, hiring first employee with EPF/ETF + tax, annual compliance calendar for a Pvt Ltd, closing a company), 5 negative (other countries' law, general non-legal questions — skills should NOT trigger), 5 written in Sinhala-English mix the way Sri Lankan founders type (e.g., "company ekak register karanna mona documents da ona").

Leave expected_nodes empty for now; we fill them after Phase 3. Do not invent legal answers — questions only.
```

**Your review gate:** read `docs/audit-baseline.md` and the eval questions; fix any unrealistic questions.

---

### Phase 1 — Ontology and schema

```
Phase 1: define the ontology. Read docs/optimization-plan.md section 1.2 and docs/audit-baseline.md.

1. Create ontology/ontology.md defining node types, edge types (with direction, e.g. obligation -ADMINISTERED_BY-> regulator), allowed source/target type pairs, ID convention, prefixes, and the <!-- kg ... --> annotation format. Include 3 fully worked examples using real content from company-secretarial.
2. Create ontology/node.schema.json (JSON Schema) for a compiled node: id, type, title, summary (≤200 chars), skill, file, line_start, line_end, edges{type:[ids]}, verified (date), source, status (current|amended|repealed|draft).
3. Propose any node/edge types the plan is missing, based on what actually appears in the content. Explain each addition briefly. Keep the ontology small — prefer fewer types.
Do not touch skills/ yet.
```

**Your review gate:** approve the ontology. Changing it later is expensive.

---

### Phase 2 — Canonical shared entities

```
Phase 2: convert shared/ into canonical entity nodes.

1. Create shared/entities/statutes.md, regulators.md, forms.md, entity-types.md, glossary.md. Each entry is an H2 section with a stable ID anchor and a kg block (e.g. statute.companies-act-2007, reg.roc, reg.ird, reg.cbsl, reg.boi, form.roc.*, entity.pvt-ltd, term.*).
2. Move content from the current shared/*.md files into these; keep old files as thin redirects for one release, noting the move in CHANGELOG.md.
3. Every glossary term links to the node that defines it (DEFINED_IN).
4. Anything you are not sure of (form numbers, act numbers, amendments) → REVIEW-TODO.md, keep original text unchanged.
```

---

### Phase 3 — Pilot: annotate one skill (company-secretarial)

```
Phase 3: pilot refactor of skills/company-secretarial only.

For each file in skills/company-secretarial/references/:
1. Split content into atomic sections: one H2 = one node = one question it answers (an obligation, a deadline, a procedure, a concept). Target 100–600 tokens per section. Split oversized sections, merge tiny fragments.
2. Add a stable ID anchor to each H2 and a <!-- kg --> block per ontology/ontology.md. Link to shared entity IDs (statute, regulator, form, entity type) instead of repeating their details.
3. Start each section with a "**TL;DR:**" line of 1–2 sentences, written only from the section's existing content.
4. Replace duplicated text with a RELATED edge + one-line pointer.
5. Put tables for deadlines/forms/penalties where the content is already list-like.

Then write scripts/check_content_preserved.py: compares the pre-refactor version (git show HEAD:path) with the new files and reports any sentence from the old text that no longer appears (normalised) anywhere in the skill. Run it and paste the result. Every missing sentence must either be restored or justified as an intentional dedupe.
```

---

### Phase 4 — Graph compiler and validators

```
Phase 4: build the graph compiler (stdlib only).

1. scripts/build_graph.py: parse all Markdown under skills/, shared/entities/, playbooks/; extract nodes (H2 anchor + kg block + TL;DR as summary + file + line range) and edges. Write:
   - graph/nodes.jsonl, graph/edges.jsonl (validated against ontology/node.schema.json)
   - skills/<skill>/references/_map.md: compact table "id | type | summary | file:lines", grouped by file, plus a short "outbound links to other skills" section
   - graph/INDEX.md: one line per node across the whole repo, grouped by skill
   Add --check mode that fails (exit 1) if generated files are out of date.
2. scripts/validate.py (merge/extend existing validate_frontmatter.py): duplicate IDs, dangling edges, disallowed type pairs, orphan nodes (no edges), sections missing TL;DR, sections over 600 tokens, SKILL.md over 150 lines, descriptions over 1024 chars, missing verified date, verified older than N days (reuse check_staleness.py logic).
3. scripts/export_graph.py: --format neo4j-csv | graphml | cypher, output to graph/exports/.
4. Run everything on the pilot skill. Show me _map.md for company-secretarial and the token size of it.
```

---

### Phase 5 — Retrieval CLI (`tools/kg.py`)

```
Phase 5: write tools/kg.py, a stdlib-only retrieval CLI over graph/nodes.jsonl and edges.jsonl.

Commands: find <query> [--skill X] [--type T] [--k 8]; node <id>; neighbors <id> [--hops 1-2] [--edge-types ...]; path <a> <b>; playbook <name>; read <id> (prints only that section's lines from the source file).

Ranking for find: BM25 over title + summary + aliases + glossary synonyms, boosted by exact ID/term match; include Sinhala-English synonyms from shared/entities/glossary.md (e.g. aliases field).
Output format: plain text, one node per line: "id | type | summary | file:lines". No JSON unless --json. Add --max-chars to cap output (default 2500).
Must work from any directory (resolve paths relative to the script) and from inside a vendored dist/<skill>/ folder.
Add tests in tests/test_kg.py using unittest.
Then add evals/retrieval_eval.py: for each query in evals/queries.jsonl with expected_nodes, run `find` and report recall@5 and recall@10. This is a cheap, LLM-free retrieval benchmark.
```

Now go back to `evals/queries.jsonl` and fill `expected_nodes` for the pilot-skill questions (you or Claude Code, then you review).

---

### Phase 6 — Rewrite SKILL.md as a router (pilot)

```
Phase 6: rewrite skills/company-secretarial/SKILL.md as a lean router (≤150 lines).

Frontmatter:
- name unchanged.
- description ≤ 90 words: what it covers + when to use it, slightly "pushy" to avoid under-triggering, including the terms users actually type (ROC, annual return, AGM, board resolution, company secretary, beneficial ownership, registers, Pvt Ltd, Sinhala-English phrasings from evals). Say "Sri Lanka" explicitly so it doesn't trigger for other jurisdictions.

Body sections:
1. Scope (in / out, with the sibling skill to use for out-of-scope items).
2. Decision tree: question pattern → node ID(s) or playbook.
3. Retrieval protocol:
   a. If code execution is available: `python tools/kg.py find "<terms>"` → `kg.py read <id>` for the 1–3 best nodes → `kg.py neighbors <id> --hops 1` only if the answer needs a form, deadline or penalty.
   b. Otherwise: read references/_map.md, then open only the listed line ranges.
   c. Never read a whole reference file unless the user asks for a full overview.
4. Answer format: direct answer first, then cited statute/provision, regulator, form, deadline, "last verified" date from the node, and the standard disclaimer from DISCLAIMER.md (one line, not the full text).
5. Hand-offs: when a neighbour node belongs to another skill, name that skill.

Measure: token size of old vs new SKILL.md, and simulate 5 eval questions by following the protocol yourself, reporting how many tokens you had to read for each.
```

**Your review gate:** compare pilot answers old vs new. If good → roll out.

---

### Phase 7 — Roll out to the other nine skills

```
Phase 7: apply Phases 3 and 6 to the remaining skills, one skill at a time, in this order: company-formation, shares-and-capital, tax-compliance, employment-law, foreign-investment, commercial-contracts, data-protection, intellectual-property, dispute-resolution.

After each skill: run check_content_preserved.py, validate.py, build_graph.py, and commit ("phase 7: <skill>"). Stop and show me a summary after every 3 skills.
Cross-skill edges must point to IDs that exist; if the target skill isn't annotated yet, add it to REVIEW-TODO.md and fix after that skill is done.
```

Tip: this phase is long — run it across several sessions.

---

### Phase 8 — Cross-domain playbooks

```
Phase 8: create playbooks/ for the most common multi-domain journeys. Use the cross-domain queries in evals/queries.jsonl to choose them. Start with:
- register a new Pvt Ltd and first-year compliance
- issue shares to a foreign investor
- hire the first employees (contracts, EPF/ETF, tax)
- annual compliance calendar for a Pvt Ltd
- sign a customer/vendor contract with personal data involved
- wind up / strike off a company

Each playbook: H2 steps in order; each step = node IDs + one-line "why", + dependencies (PREREQUISITE_OF). Playbooks are nodes of type playbook with STEP_OF edges. Only reference existing nodes — no new legal content here. Add playbook routing lines to the relevant SKILL.md decision trees. Rebuild the graph and extend retrieval_eval.py to check that each cross-domain query surfaces its playbook in the top 3.
```

---

### Phase 9 — Packaging (self-contained skills + plugin)

```
Phase 9: packaging.

1. scripts/build_dist.py: for each skill produce dist/<skill>/ containing SKILL.md, references/ (incl. _map.md), tools/kg.py, and graph/ with that skill's nodes + 1-hop neighbour nodes from other skills as "stub" nodes (summary + "use skill <name>"). Rewrite any path so nothing points outside the folder. Also zip each as dist/<skill>.zip for claude.ai upload.
2. Also produce dist/srilanka-business-law-all/ — all skills + full graph — for users who want everything.
3. Check the current Claude Code plugin / marketplace documentation (don't rely on memory of the format) and add the manifest files needed so users can install the whole set as a Claude Code plugin from this GitHub repo.
4. Test: copy one dist skill to a temp dir, run kg.py find/read from there, confirm it works with no repo around it.
5. Update README.md install section for: claude.ai upload, Claude Code (~/.claude/skills), plugin install, and "use the graph in your own GraphRAG" (exports).
```

---

### Phase 10 — CI, llms.txt, docs

```
Phase 10:
1. .github/workflows/ci.yml: on PR run validate.py, build_graph.py --check, check links, tests, retrieval_eval.py (fail if recall@10 drops below the current baseline stored in evals/baseline.json), and a token-budget check (SKILL.md ≤150 lines, description ≤1024 chars, sections ≤600 tokens).
2. Add a scheduled weekly workflow running check_staleness.py that opens an issue listing nodes whose "verified" date is older than 180 days.
3. Create llms.txt at the root: project summary, how the content is organised, links to graph/INDEX.md, ontology, playbooks, and disclaimer.
4. Update docs/architecture.md, docs/skill-authoring-guide.md (how to add a node, IDs, kg block, TL;DR rule), CONTRIBUTING.md, and add a PR template checklist.
5. CHANGELOG.md entry + version bump (breaking change for anyone linking to old shared/ paths).
```

---

### Phase 11 — Measure and tune

```
Phase 11: evaluation.
1. Run audit_tokens.py again → docs/audit-after.md, with a before/after comparison table (always-loaded tokens, typical tokens per answered query, number of files read per query).
2. Run retrieval_eval.py and store results in evals/baseline.json.
3. Use the skill-creator skill's description optimisation loop on each SKILL.md description with the trigger queries from evals/queries.jsonl (including negative and Singlish ones). Show me before/after descriptions and trigger scores; don't apply without my approval.
```

---

## 4. Success metrics

| Metric | How measured | Target |
|---|---|---|
| Always-loaded tokens (10 descriptions) | audit_tokens.py | ≤ ~1,300 |
| Tokens read per single-domain answer | Phase 6/11 simulation | 60–80% lower than baseline |
| Retrieval recall@10 (LLM-free) | retrieval_eval.py | ≥ 0.9 |
| Cross-domain queries hitting the right playbook in top 3 | retrieval_eval.py | ≥ 0.9 |
| Correct skill triggering, negatives not triggering | skill-creator trigger eval | ≥ 0.9 / ≤ 0.1 |
| Dangling edges / orphan nodes | validate.py | 0 |

## 5. Decisions to make before starting

1. **10 domain skills vs one umbrella skill.** Recommendation: keep 10 (better triggering precision, cheaper per-query loads), and let the graph + playbooks handle cross-domain questions. Revisit only if evals show cross-domain questions often trigger just one skill.
2. **Embeddings / vector search:** keep them out of the skills (no dependencies, deterministic). If you later build a hosted GraphRAG service, generate embeddings from `graph/nodes.jsonl` in a separate project.
3. **Content verification:** every node carries `verified` and `source`. The refactor is a good moment to get a lawyer to review `REVIEW-TODO.md`, but that review is separate from the structural work.
