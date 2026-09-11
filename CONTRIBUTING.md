# Contributing

Thank you — corrections to Sri Lankan legal content are genuinely scarce and genuinely useful.

You do **not** need to be a lawyer to contribute. You do need to cite your source.

---

## The one rule

> **Every factual claim cites a primary source, or it is labelled as unverified.**

A primary source is: the statute text, a gazette, a regulator's own website or circular, a
reported judgment, or an official form. A client alert from a professional firm is a
*secondary* source — useful for finding things, not sufficient on its own for a rate, a
threshold or a commencement date.

Why this is strict: in 2026 several firms published alerts stating the VAT registration
threshold had dropped to LKR 36m. The proposal was dropped before enactment. If we had
relied on secondary sources we would have told businesses to register when they need not.

---

## Ways to contribute

### 1. Report an error (most valuable)

Open an issue with the **Legal accuracy** template. Include:
- the file and line,
- what it says,
- what it should say,
- your source.

If the error could cause a missed deadline or a penalty, label it `priority:critical`.

### 2. Update something that changed

Sri Lankan law moves. Budget measures land in November, most tax changes bite on 1 April,
labour figures often change on 1 January, and commencement gazettes appear without warning.
Use the **Amendment update** issue template or go straight to a PR.

### 3. Add a new skill or reference file

Open a **New skill proposal** issue first so we can agree the scope and avoid two people
writing the same thing.

### 4. Translate

Sinhala and Tamil versions are wanted. Translations live under `i18n/si/` and `i18n/ta/`
mirroring the English tree. Translate the content, not the citations — statute names and
section numbers stay in English so they remain searchable.

---

## File format

Every reference file starts with frontmatter:

```yaml
---
title: Annual return (Form 15)
skill: sl-company-secretarial
last_verified: 2026-09-11
verification_status: verified
primary_sources:
  - "Companies Act No. 7 of 2007, s 131"
  - "https://drc.gov.lk/en/?page_id=1998"
---
```

`verification_status` is one of:

| Status | Meaning |
|---|---|
| `verified` | Every material claim checked against a primary source on `last_verified` |
| `partial` | Core position verified; some detail from secondary sources — flagged inline |
| `needs-verification` | Drafted from general knowledge. Honest placeholder, not authority |

Anything `needs-verification` must carry this banner immediately after the frontmatter:

```markdown
> ⚠️ **Unverified draft.** Not checked against primary sources. Do not rely on figures,
> dates or form numbers in this file without confirming them.
```

---

## Citation format

Use the Sri Lankan convention.

**Statutes** — full title, number, year, then section:

> Companies Act, No. 7 of 2007, s 58(1)
> Inland Revenue Act, No. 24 of 2017, s 85 (as amended by Act No. 2 of 2025)

**Amendments** — always name the amending Act and the effective date:

> raised to 45% by the Inland Revenue (Amendment) Act, No. 2 of 2025, w.e.f. 1 April 2025

**Gazettes** — number, sub-number, date:

> Extraordinary Gazette No. 2480/48 of 21 March 2026

**Cases** — party names, year, report, page:

> *Peiris v. Ceylon Cold Stores Ltd* (1996) 2 Sri LR 121

**Regulator pages** — full URL plus the date you accessed it, because Sri Lankan government
sites reorganise often and links rot.

More detail in [docs/verification-policy.md](docs/verification-policy.md).

---

## Writing style

These files get read in a hurry, often out of context. So:

- **Lead with the answer.** The obligation first, the background second.
- **Use tables for anything with rates, deadlines or thresholds.**
- **Imperative for procedure.** "File Form 6 within 20 working days", not "It is advisable that a company should file...".
- **Flag the trap.** Where practitioners commonly get something wrong, say so explicitly.
- **Don't pad.** No "in today's dynamic business environment". Delete it.
- **Never state a figure without its effective date.** A rate without a date is useless in a year.

---

## What we won't merge

- Content without sources and without an honest `needs-verification` label
- Anything that reads as advice to a specific person or entity
- Full reproduction of statutory text (cite and link instead — it's Crown material and it bloats the repo)
- Firm marketing, referral links, or "contact us for a consultation" content
- Templates presented as ready to sign without review
- Scraped content from paid legal databases

---

## Review process

1. Open a PR against `main`. Small and focused beats large and sweeping.
2. Fill the PR template, including the source for every changed figure.
3. One maintainer review for content; a second review is required for anything in
   `tax-compliance/` or `employment-law/`, because errors there have direct financial consequences.
4. On merge, update `last_verified` — the reviewer will ask if you forgot.

Critical accuracy fixes are merged as fast as they can be checked. Everything else waits its turn.

---

## Code of conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Disagreements about what the law says are
welcome and expected — argue from sources, not from seniority.
