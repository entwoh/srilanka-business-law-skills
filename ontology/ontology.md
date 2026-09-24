---
title: Knowledge-graph ontology
last_verified: 2026-09-24
status: proposed — awaiting maintainer approval (Phase 1 review gate)
---

# Knowledge-graph ontology

This file defines what a **node** and an **edge** are in this repository, how node IDs are
formed, and how a Markdown section declares its node. `scripts/build_graph.py` (Phase 4)
compiles every annotated section into `graph/nodes.jsonl` and `graph/edges.jsonl`.
`scripts/validate.py` enforces the rules below. The tables in §3 and §4 are parsed by the
validator, so keep their format: one row per type, type names in backticks.

Markdown stays the single source of truth. The graph is generated from it and never edited
by hand.

## 1. Principles

1. **One H2 = one node = one question it answers.** H3s inside an H2 belong to that node.
   The H1 is the file title and is not a node.
2. **Every line of body text belongs to exactly one node.** Text between the H1 and the first
   H2 (for example a warning box) must be moved into an H2 node, usually
   `<prefix>.<topic>.overview`. Otherwise retrieval cannot reach it.
3. **Edges describe what the text already says.** An annotation may only assert a
   relationship that the section's own text (or the file's frontmatter sources) supports. If
   an edge would need new legal knowledge, leave it out and log it in `REVIEW-TODO.md`.
   Annotating is not a way to add law.
4. **No pinpoint without a source.** A `cites` edge carries a section number only if the text
   gives one. Much of the current content says "verify the section number", so most citations
   point at the whole statute.
5. **Few types, rich text.** The graph routes the reader to the right section. It does not
   replace the section. When in doubt, use `concept` plus a `related` edge.

## 2. Node IDs

```
<prefix>.<topic>.<slug>        domain nodes (exactly 3 segments)
<prefix>.<slug>[.<slug>]       shared entities and playbooks (2–3 segments)
```

- Lowercase ASCII, digits and hyphens inside a segment; segments separated by dots.
  Regex: `^[a-z]+(\.[a-z0-9][a-z0-9-]*){1,2}$`.
- **Permanent.** An ID is never renamed and never reused, even if the section moves to
  another file. If a node's meaning changes, create a new ID and add `supersedes: [<old>]`.
  The old node stays, with `status: repealed` or `amended`.
- `<topic>` is normally the reference file stem at the time the node is created
  (`cs.annual-return.*`). It is not updated if the file is later renamed.
- `<slug>` names the question, not the heading wording: `deadline`, `which-form`,
  `late-filing`, `company-duties`.

### Prefixes

| Prefix | Owner | Example |
|---|---|---|
| `cf` | company-formation | `cf.incorporation-checklist.name-reservation` |
| `cs` | company-secretarial | `cs.annual-return.deadline` |
| `sc` | shares-and-capital | `sc.share-issues.form-6` |
| `cc` | commercial-contracts | `cc.formation-and-execution.stamp-duty` |
| `emp` | employment-law | `emp.termination.tewa` |
| `tax` | tax-compliance | `tax.vat-and-sscl.threshold` |
| `fi` | foreign-investment | `fi.exchange-control.iia` |
| `ip` | intellectual-property | `ip.trade-marks.classes` |
| `dp` | data-protection | `dp.pdpa-obligations.commencement` |
| `dr` | dispute-resolution | `dr.insolvency.solvent-closure` |
| `statute` | shared/entities/statutes.md | `statute.companies-act-2007` |
| `reg` | shared/entities/regulators.md | `reg.roc` |
| `form` | shared/entities/forms.md | `form.roc.15`, `form.roc.bo5` |
| `entity` | shared/entities/entity-types.md | `entity.pvt-ltd` |
| `term` | shared/entities/glossary.md | `term.beneficial-owner` |
| `pb` | playbooks/ | `pb.foreign-investor-share-issue` |

Shared-entity slug rules:

- **Statutes:** `statute.<short-title-slug>-<year>`, e.g. `statute.companies-act-2007`,
  `statute.companies-amendment-act-2025`, `statute.inland-revenue-act-2017`. Add `-no<N>`
  only if two instruments would collide (`…-2025-no2`). Regulations and bills use the same
  rule (`statute.companies-bo-regulation-2026`).
- **Forms:** `form.<issuer>.<number>`: the ROC form number in lowercase, no spaces
  (`form.roc.15a`, `form.roc.26b`, `form.roc.bo5`). Other issuers use a slug
  (`form.ird.<slug>`).
- **Regulators:** a short conventional acronym or slug (`reg.roc`, `reg.ird`, `reg.cbsl`,
  `reg.labour-dept`, `reg.labour-tribunal`).

## 3. Node types

| Type | Meaning | Typical content | Extra fields |
|---|---|---|---|
| `statute` | An Act, Ordinance, Law, Regulation, gazetted instrument, Bill, or the uncodified common law | Title, number, year, subject, commencement status | `kind` |
| `regulator` | An authority, office or forum that administers, receives filings or decides disputes (includes courts and tribunals) | Remit, portal, where to file | `kind` |
| `form` | A prescribed form or filing | Number, purpose, eROC-generated or not | — |
| `entity_type` | A kind of business vehicle or status a rule can apply to | Pvt Ltd, PLC, guarantee company, overseas company, sole proprietorship, partnership, BOI enterprise | — |
| `concept` | A definition, principle, distinction or trap. The default type. | "Who is a beneficial owner", "transfer is not issue" | — |
| `obligation` | Something a person or company must do | "Maintain a BO register", "file the annual return" | — |
| `deadline` | When an obligation falls due, including transitional windows | "First annual return within 18 months" | — |
| `procedure` | An ordered how-to or checklist | "Practical sequence", "closing checklist" | — |
| `penalty` | A consequence of non-compliance: fine, offence, personal liability, strike-off | "Late filing" | — |
| `rate` | A rate, threshold or fixed amount that changes by law over time | VAT threshold, EPF %, minimum wage, corporate tax rate | `effective` (required) |
| `playbook` | A pre-computed cross-domain path: an ordered list of existing nodes | "Issue shares to a foreign investor" | `steps` (required) |

`kind` values. **statute:** `act`, `ordinance`, `law`, `regulation`, `gazette`, `bill`,
`common-law`. **regulator:** `authority`, `court`, `tribunal`, `registry`, `portal`.

**Umbrella entity.** `entity.company` means "any company incorporated under the Companies
Act". An `applies_to: [entity.company]` edge matches every company entity type. Use it when
the text says a rule applies to every company, rather than listing each type.

## 4. Edge types

Edges are declared **on the source node** in its `kg` block, using the lowercase edge name as
the key (`requires_form: [...]`). The only exception is `steps:` on a playbook (see below).

| Edge | Direction (source → target) | Allowed source types | Allowed target types | Meaning |
|---|---|---|---|---|
| `CITES` | node → statute | any except `statute`, `regulator`, `playbook` | `statute` | The text relies on this instrument. Optional pinpoint after `#`. |
| `ADMINISTERED_BY` | node → regulator | `statute`, `obligation`, `deadline`, `procedure`, `form`, `penalty`, `rate` | `regulator` | Who administers, receives or decides it |
| `REQUIRES_FORM` | node → form | `obligation`, `deadline`, `procedure` | `form` | Complying needs this form |
| `HAS_DEADLINE` | node → deadline | `obligation`, `procedure`, `form` | `deadline` | When it falls due |
| `APPLIES_TO` | node → entity_type | `concept`, `obligation`, `deadline`, `procedure`, `penalty`, `rate`, `form` | `entity_type` | Scope: which vehicles the rule covers |
| `TRIGGERS` | node → obligation/deadline | `procedure`, `concept`, `rate` | `obligation`, `deadline` | Doing/reaching the source creates the target duty (e.g. a share issue triggers a BO update; crossing the VAT threshold triggers registration) |
| `PREREQUISITE_OF` | node → node | `obligation`, `procedure`, `form`, `deadline` | `obligation`, `procedure`, `form` | Source must be done before target |
| `DEFINED_IN` | term → node | `concept` | `concept`, `statute`, `obligation`, `rate` | Where the authoritative definition lives (used by glossary terms) |
| `PENALISED_BY` | node → penalty | `obligation`, `deadline` | `penalty` | Consequence of not complying |
| `AMENDED_BY` | statute → statute | `statute` | `statute` | Later instrument amends the source |
| `SUPERSEDES` | new → old | any | same type as source | Replaces an old node or ID (§2) |
| `RELATED` | node ↔ node | any | any | See-also. **Symmetric**: declare once; compiled both ways. Use it for dedupe pointers and cross-skill hand-offs. |
| `STEP_OF` | node → playbook | any except `playbook` | `playbook` | Node is a step in the playbook. Carries `order`. |

Edges have no "reverse" keys (there is no `penalises:`). Traversal in either direction is a
query-time concern (`kg.py neighbors`).

**Pinpoints.** A `cites` target may carry a pinpoint after `#`: `#s107`, `#ss130A-130J`,
`#part-vi`, `#sch1`. The compiler splits it into the edge's `pinpoint` attribute. The target
node is always the whole statute. There are no per-section nodes (see §8, change 2).

## 5. Annotation format

```markdown
## <Heading text> {#<node-id>}
<!-- kg
type: <node type>
<edge_key>: [<id>, <id>#<pinpoint>]
aliases: [<search synonym>, <Singlish phrasing>]
tags: [trap]
verified: YYYY-MM-DD
source: [<official URL or citation>]
status: current
-->
**TL;DR:** One or two sentences, ≤200 characters, written only from this section's own text.

<existing section content>
```

Rules:

- The `{#id}` anchor goes at the end of the H2 line. The `<!-- kg ... -->` block goes on the
  lines directly after it. The **TL;DR** line comes directly after the block and becomes the
  node's `summary`.
- The block uses a tiny YAML subset that a stdlib parser can read: `key: value` and
  `key: [a, b, c]` on one line. No nesting and no multi-line values.
- **Inherited defaults.** `verified`, `source` and `verification` default to the file's
  frontmatter (`last_verified`, `primary_sources`, `verification_status`). Set them in the
  block only when the section differs from the file (for example, one section re-verified
  later). `status` defaults to `current`.
- `title` is the heading text without the anchor.
- `aliases` feed `kg.py find`. Use them for vernacular and Singlish ("BR", "Form 20 karanna",
  "UBO") and for the ways statutes are actually written ("VAT (Amendment) Act 2026").
- `tags` is a free list. Recognised tags: `trap` (a known practitioner mistake),
  `fast-moving` (review more often than every 180 days), `contested` (credible sources
  disagree; the text says so).

### Node fields that are not edges

| Field | Values | Notes |
|---|---|---|
| `type` | §3 | required |
| `status` | `current` · `amended` · `repealed` · `proposed` · `not_in_force` | Legal currency of what the node describes. `proposed` = Bill or budget proposal, not law. `not_in_force` = enacted but not yet commenced (in whole or part). |
| `verification` | `verified` · `partial` · `needs-verification` | Confidence in *our* text. Same scale as the existing frontmatter. |
| `verified` | date | Last checked against a primary source |
| `source` | list | Primary sources for this node |
| `effective` | date | Required for `rate`: the date from which the figure applies |
| `steps` | ordered list of IDs | Required for `playbook`; compiled to `STEP_OF` edges with `order` 1…n |
| `kind` | §3 | `statute` and `regulator` only |

### Playbooks

A playbook file is **one node** of type `playbook`. Its `steps:` list gives the order, and
each step is an H3 inside that node with a one-line "why". Reading the playbook is therefore
a single `kg.py read`. Playbooks may only reference existing node IDs. They carry no legal
content of their own. Dependencies between steps are `prerequisite_of` edges declared on the
domain nodes themselves, where the supporting text lives.

## 6. Compiled output

`graph/nodes.jsonl`: one object per node, validated against
[`node.schema.json`](node.schema.json).

`graph/edges.jsonl`: one object per edge, validated against
[`edge.schema.json`](edge.schema.json):

```json
{"src": "cs.annual-return.which-form", "type": "REQUIRES_FORM", "dst": "form.roc.15"}
{"src": "cs.beneficial-ownership.company-duties", "type": "CITES", "dst": "statute.companies-act-2007", "pinpoint": "ss130A-130J"}
{"src": "sc.share-issues.mechanics", "type": "STEP_OF", "dst": "pb.foreign-investor-share-issue", "order": 3}
```

`RELATED` edges are written once with `"symmetric": true`.

## 7. Worked examples (company-secretarial)

These examples use the current text of
`skills/company-secretarial/references/annual-return.md` and `beneficial-ownership.md`. Only
headings, anchors, `kg` blocks and TL;DR lines are added. The body text is unchanged. IDs for
shared entities (`statute.*`, `reg.*`, `form.*`, `entity.*`) are the ones Phase 2 will
create.

### Example 1: an obligation (annual-return.md, "Which form", lines 13–20)

```markdown
## Filing the annual return — which form {#cs.annual-return.which-form}
<!-- kg
type: obligation
cites: [statute.companies-act-2007]
administered_by: [reg.roc]
requires_form: [form.roc.15, form.roc.15a]
has_deadline: [cs.annual-return.deadline]
penalised_by: [cs.annual-return.late-filing]
aliases: [F15, Form 15, annual return eka]
-->
**TL;DR:** Companies with share capital file Form 15; companies limited by guarantee file
Form 15A.

| Company type | Form |
|---|---|
| Company with share capital (the normal case) | **Form 15** |
| Company limited by guarantee | **Form 15A** |

The ROC operates a dedicated **F15 branch** — it is one of the two highest-volume filings.
```

The `has_deadline` and `penalised_by` targets are sibling nodes in the same file. There is
no `applies_to`: the table already splits the rule by company type through the two forms,
and the form nodes carry that scope.

### Example 2: a deadline (annual-return.md, "When it's due", lines 22–29)

```markdown
## When the annual return is due {#cs.annual-return.deadline}
<!-- kg
type: deadline
cites: [statute.companies-act-2007]
administered_by: [reg.roc]
tags: [trap]
aliases: [first annual return, 18 months]
-->
**TL;DR:** First annual return within 18 months of incorporation, then annually. Confirm the
anniversary basis for later years against the Act and ROC guidance.

- **First annual return: within 18 months of incorporation.** Not twelve. Not the first
  anniversary. This is the single most commonly missed company deadline in Sri Lanka.
- **Thereafter: annually.**

Confirm the exact anniversary basis for subsequent years against the Act and the ROC's own
guidance — practice on the reference date has varied.
```

No `applies_to` here: this section's text does not say which companies it covers, so
principle 3 leaves the edge out, even though it is probably "every company".

Compiled node (`verified`, `source` and `verification` inherited from the frontmatter):

```json
{"id": "cs.annual-return.deadline", "type": "deadline",
 "title": "When the annual return is due",
 "summary": "First annual return within 18 months of incorporation, then annually. Confirm the anniversary basis for later years against the Act and ROC guidance.",
 "skill": "company-secretarial", "file": "skills/company-secretarial/references/annual-return.md",
 "line_start": 28, "line_end": 42,
 "edges": {"CITES": ["statute.companies-act-2007"], "ADMINISTERED_BY": ["reg.roc"]},
 "aliases": ["first annual return", "18 months"], "tags": ["trap"],
 "verified": "2026-09-11", "source": ["Companies Act, No. 7 of 2007", "https://drc.gov.lk/en/?page_id=1998 (accessed 11 September 2026)"],
 "status": "current", "verification": "partial"}
```

### Example 3: an obligation with a pinpoint and a cross-skill link (beneficial-ownership.md, "What companies must do", lines 54–61)

```markdown
## What companies must do {#cs.beneficial-ownership.company-duties}
<!-- kg
type: obligation
cites: [statute.companies-act-2007#ss130A-130J, statute.companies-amendment-act-2025, statute.companies-bo-regulation-2026]
administered_by: [reg.roc]
requires_form: [form.roc.bo5]
has_deadline: [cs.beneficial-ownership.deadlines]
penalised_by: [cs.beneficial-ownership.consequences]
applies_to: [entity.company]
aliases: [UBO register, BO register, beneficial ownership filing, BO form eka]
-->
**TL;DR:** Identify beneficial owners through every layer, keep a BO register, appoint a
Sri Lanka-resident authorised person (Form BO 5), and file with the ROC, keeping it current.

1. **Identify** the beneficial owners, tracing through any corporate or nominee layers.
2. **Maintain a beneficial ownership register** with the prescribed particulars.
3. **Appoint an authorised person** — a natural person **resident in Sri Lanka** responsible
   for safekeeping the register and making details available to authorities. Notified using
   **Form BO 5**.
4. **File with the ROC** and keep the filing current as ownership changes.
```

Where the edges come from: the pinpoint `ss130A–130J` is in the file's own text (line 21).
`applies_to: [entity.company]` rests on "it applies to every company" (line 15). The
connection to share transactions ("the BO position changes with it — update the register as
part of closing", line 110) is declared on the **source** side, as a `triggers` edge on the
shares-and-capital share-issue node when that skill is annotated:

```markdown
## Mechanics {#sc.share-issues.mechanics}
<!-- kg
type: procedure
triggers: [cs.beneficial-ownership.company-duties]
...
```

Until `sc.*` exists, that edge is logged in `REVIEW-TODO.md` (Phase 7 rule).

## 8. Changes from the plan's draft ontology (for review)

The plan (§1.2) proposed 11 node types and 13 edge types. After reading the content, this
ontology keeps 11 node types and all 13 edge types, with these changes:

1. **Added `rate`.** Rates, thresholds and fixed amounts (VAT threshold, EPF 12% / 8%, ETF
   3%, minimum wage, corporate tax rates) are the most error-prone, fastest-moving facts in
   the repo. Rule 1 of the authoring guide is "never state a rate without its effective
   date". A dedicated type with a required `effective` field lets the validator enforce
   that, and lets staleness checks target the right nodes.
2. **Dropped `provision`.** Most section numbers in the content are still marked "verify".
   Per-section nodes would be mostly empty orphans, and they would fix unverified section
   numbers into permanent IDs. Pinpoints live on `CITES` edges instead (`#ss130A-130J`).
   `provision` can be added later without breaking any ID.
3. **No separate `event` type**, although `TRIGGERS` was described as "event → obligation".
   The events in the content (a share issue, a director resigning, crossing the VAT
   threshold) are already `procedure`, `concept` or `rate` nodes, so those types are the
   allowed `TRIGGERS` sources.
4. **Status split into two fields.** The plan's `status: current|amended|repealed|draft`
   uses "draft" for legal currency. The repo already uses "draft" to mean *our text is
   unverified* (the "Unverified draft" banner). To keep the two apart:
   `status` = `current|amended|repealed|proposed|not_in_force` (legal currency; covers the
   Inland Revenue Bill and PDPA commencement), and `verification` =
   `verified|partial|needs-verification` (our confidence; carried over from frontmatter).
5. **Glossary terms are `concept` nodes** with the `term.` prefix, not a separate type.
6. **Courts and tribunals are `regulator` nodes** (`kind: court|tribunal`). The name stays
   `regulator` because that is what the shared index already calls them.
7. **Added `pb.` prefix** for playbooks, and each playbook is one node (§5) so that reading
   it costs one call.
8. **Added fields** `aliases`, `tags`, `verification`, `effective`, `steps`, `kind`.
9. **Umbrella `entity.company`** instead of an `IS_A`/`BROADER` edge type.

### Open questions for the maintainer

- **`{#id}` renders literally on GitHub.** GitHub does not support custom heading IDs, so
  readers will see `{#cs.annual-return.deadline}` at the end of each heading. The plan's
  format is kept because it makes IDs grep-able and visible in `kg.py read` output. The
  alternative is `id:` inside the `kg` block, which is invisible on GitHub but harder to grep.
- **Unverified-draft banners.** The audit recommends replacing the per-file banner prose
  with `verification: needs-verification` plus a mandatory caveat in the SKILL.md answer
  format. That changes how a legal warning is surfaced, so it needs explicit sign-off.
