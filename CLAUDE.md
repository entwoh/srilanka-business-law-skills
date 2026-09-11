# CLAUDE.md

Instructions for Claude Code working in this repository.

## What this repo is

A knowledge base of Sri Lankan business law, structured as Claude Skills. Read
[README.md](README.md) for the layout and [docs/architecture.md](docs/architecture.md) for why
it is split the way it is.

**This content is used to answer legal questions.** A wrong rate, threshold, form number or
commencement date can cause a real person to miss a statutory deadline or incur penalties.
Optimise for accuracy over completeness, and for honest gaps over confident filler.

## The one rule that overrides everything

> **Never upgrade a file's `verification_status` unless you have actually checked a primary
> source in this session.**

`verification_status` is one of `verified`, `partial`, `needs-verification`. It is not a
quality score and not a to-do marker — it is a factual claim about what has been checked.

- Do **not** change `needs-verification` → `verified` because the content looks good.
- Do **not** remove the ⚠️ banner from a `needs-verification` file while rewriting it.
- Do **not** set `last_verified` to today unless you verified it today.

If asked to "clean up" or "improve" files, improve wording and structure and leave the
verification metadata exactly as it is.

## Source hierarchy

Tier 1 (statute text, gazettes) and tier 2 (regulator sites: drc.gov.lk, ird.gov.lk,
dpa.gov.lk, cbsl.gov.lk) are the only sources that support `verified`. Firm client alerts and
EOR guides are leads, not authority — see [docs/verification-policy.md](docs/verification-policy.md).

**Bill ≠ Act. Act ≠ in force.** Before recording any change, confirm: is it a proposal, is the
Bill enacted, is the Act commenced, and is *all* of it commenced. Two failures are documented
in the verification policy; read them before doing tax or data-protection work.

## Editing rules

- Every rate, threshold or figure states its **effective date**. No exceptions.
- Never reproduce full statutory text. Cite the section and link.
- Citation format is in [CONTRIBUTING.md](CONTRIBUTING.md). Use it.
- One file owns a topic; others link. Do not duplicate content across skills — the overlap
  table in `docs/architecture.md` says who owns what.
- `SKILL.md` frontmatter needs `name` and `description`. Reference files need `title`,
  `last_verified`, `verification_status`, and `primary_sources` if `verified`.
- Keep `SKILL.md` under ~500 lines; push detail into `references/`.

## Before committing

```bash
python scripts/validate_frontmatter.py    # must pass
python scripts/check_staleness.py         # warns only
```

Also check that relative links resolve — several files cross-reference each other and the
depth is easy to get wrong (`../../` from `skills/x/references/` lands in `skills/`, not root).

Update [CHANGELOG.md](CHANGELOG.md) if the legal position changed, using the
`LAW` / `FIX` / `ADD` / `VERIFY` markers.

## Review requirements

Changes under `skills/tax-compliance/` or `skills/employment-law/` need **two** human
approvals before merge. Flag this in the PR description rather than assuming one review is
enough.

## Things not to do

- Do not write content that reads as advice to a specific person or entity.
- Do not add firm marketing, referral links, or "contact us" content.
- Do not delete a ⚠️ conflict flag because you found one source that resolves it. Two credible
  sources disagreeing is worth recording until a primary source settles it.
- Do not silently pick a side on a contested point. Say it is contested.

## Current state

- 2 files `verified`, 15 `partial`, 18 `needs-verification`
- `<your-org>` placeholders remain in README.md and LICENSE-CONTENT.md
- MAINTAINERS.md is a template with vacant roles
- Highest-value work is in [docs/roadmap.md](docs/roadmap.md) under "Now"
