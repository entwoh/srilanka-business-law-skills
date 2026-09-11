---
title: Skill authoring guide
last_verified: 2026-09-11
---

# Skill authoring guide

How skills in this repository are structured, and why.

## Anatomy

```
skills/<skill-name>/
├── SKILL.md              # required — entry point
└── references/           # loaded only when needed
    ├── topic-a.md
    └── topic-b.md
```

`SKILL.md` carries YAML frontmatter with `name` and `description`, then a markdown body.

## Progressive disclosure

An assistant loads a skill in three stages:

1. **Name + description** — always in context. This is what decides whether the skill fires.
2. **`SKILL.md` body** — loaded when the skill fires. Keep under ~500 lines.
3. **`references/` files** — loaded only when `SKILL.md` points to them.

This is why reference files are split by topic rather than kept in one large document. Someone
asking about a share transfer shouldn't pay the context cost of the gratuity rules.

## Writing the description

The description is the trigger. Models under-trigger skills, so descriptions here are
deliberately assertive about when to fire, and name the concrete phrases a user would actually
use.

**Weak:**
> Information about Sri Lankan company law.

**Strong:**
> Sri Lankan company secretarial compliance under the Companies Act No. 7 of 2007 — annual
> returns (Form 15), board and shareholder meetings, written resolutions, statutory registers,
> beneficial ownership filings, and directors' duties. Use this whenever the user mentions a
> Sri Lankan company's filings, ROC forms, annual return, AGM, board resolution, company
> secretary, beneficial owner or UBO register — including when they just say "my company in
> Colombo needs to file something" without naming the form.

Name the statute, the forms, and the vernacular. "ROC", "BR certificate", "Form 20", "EPF
number" are how people actually talk about this.

## Writing the SKILL.md body

Structure that works for legal skills:

```markdown
# <Skill name>

## Before anything else
The scope limit and the "get an Attorney-at-Law" line. Stated once, at the top, so it
doesn't have to be repeated in every answer.

## What to establish first
The 3–5 facts that change the answer. For a company matter: private or public? how many
shareholders? any foreign shareholding? BOI status?

## Workflow
Numbered steps.

## Reference files
| File | Read when |
|---|---|
| `references/x.md` | the question involves X |

## Common traps
The things practitioners get wrong.
```

## Why "what to establish first" matters most

Sri Lankan business law branches hard on a few facts:

- **Private vs public vs listed** — governance and disclosure differ completely.
- **Foreign shareholding** — triggers exchange control, sectoral limits, possibly BOI.
- **BOI enterprise or not** — different tax and labour treatment.
- **Employee headcount ≥ 15** — turns on TEWA and statutory gratuity.
- **Turnover thresholds** — VAT and SSCL registration.
- **Beneficial ownership ≥ 10%** — disclosure obligations.

A skill that answers before establishing these gives a confidently wrong answer. Build the
question into the workflow.

## Rules specific to this repository

1. **Never state a rate without its effective date.**
2. **Point at forms by number and link to the ROC forms page**, which is the only list that
   stays current.
3. **Prefer a checklist to prose** for anything procedural.
4. **Surface the trap.** If a practitioner would say "ah, but watch out for—", write that down.
5. **Don't write advice.** Write the framework and the source, then tell the user to take it
   to an Attorney-at-Law.

## Testing a skill

Write 3–5 realistic prompts in the voice of an actual user — a founder, an accountant, an
operations manager. Not "explain s 58 of the Companies Act", but:

> "we're bringing in an investor for 20% of my company, what do I need to file"

Run them and check: did the right reference file get read? Did it ask about foreign
shareholding before answering? Did it cite sections? Did it flag the beneficial ownership
filing?

Store prompts in `skills/<name>/evals/evals.json`.
