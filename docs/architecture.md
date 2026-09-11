---
title: Repository architecture
last_verified: 2026-09-11
---

# Architecture

## Layout

```
srilanka-business-law-skills/
├── README.md                 CONTRIBUTING.md      CHANGELOG.md
├── DISCLAIMER.md             CODE_OF_CONDUCT.md
├── LICENSE (MIT)             LICENSE-CONTENT.md (CC BY 4.0)
├── .github/                  issue + PR templates, CI
├── docs/                     how the project works
│   ├── architecture.md
│   ├── skill-authoring-guide.md
│   ├── verification-policy.md
│   └── roadmap.md
├── shared/                   cross-cutting indexes
│   ├── statutes-index.md
│   ├── regulators-index.md
│   ├── roc-forms-index.md
│   └── glossary.md
├── scripts/                  CI helpers
└── skills/                   the ten skills
    └── <skill>/
        ├── SKILL.md
        └── references/
```

## Why ten skills rather than one

A single "Sri Lankan business law" skill would either be too shallow to help or too large to
load. The split follows how questions actually arrive: someone asking about a termination is
not simultaneously asking about trade marks.

The boundaries are drawn on **statutory lines**, not topic vibes, so each skill has a clear
governing Act and a clear regulator:

| Skill | Principal statute | Regulator |
|---|---|---|
| company-formation | Companies Act No. 7 of 2007 | ROC |
| company-secretarial | Companies Act No. 7 of 2007 | ROC |
| shares-and-capital | Companies Act No. 7 of 2007 | ROC / SEC |
| employment-law | Shop & Office Act, TEWA, EPF, ETF, Gratuity | Dept. of Labour |
| tax-compliance | Inland Revenue Act No. 24 of 2017, VAT Act | IRD |
| commercial-contracts | Roman-Dutch common law, Sale of Goods, Stamp Duty | — |
| foreign-investment | BOI Law, Foreign Exchange Act No. 12 of 2017 | BOI / CBSL |
| intellectual-property | IP Act No. 36 of 2003 | NIPO |
| data-protection | PDPA No. 9 of 2022 | DPA |
| dispute-resolution | Civil Procedure Code, Arbitration Act | Courts |

## Deliberate overlaps

Some topics sit across skills. The rule is: **one file owns it; others link.**

| Topic | Owned by | Linked from |
|---|---|---|
| Share issue mechanics | shares-and-capital | company-secretarial, foreign-investment |
| Beneficial ownership | company-secretarial | company-formation, shares-and-capital |
| Stamp duty on share transfers | shares-and-capital | commercial-contracts |
| EPF/ETF registration | employment-law | company-formation |
| Inward Investment Accounts | foreign-investment | shares-and-capital |
| Employee tax (APIT) | tax-compliance | employment-law |

Duplicating content across skills is how a knowledge base rots: one copy gets updated and the
other doesn't. Link instead.

## The shared layer

`shared/` holds material that nearly every skill needs:

- **statutes-index.md** — one row per statute: number, year, subject, amendments, status.
  The single place to check "is this still current".
- **roc-forms-index.md** — the complete ROC forms list. Form numbers are the most commonly
  mis-stated fact in Sri Lankan company guidance.
- **regulators-index.md** — who administers what, and where to file.
- **glossary.md** — including the local vernacular ("BR certificate", "Form 20 branch").

## Design constraints

1. **Offline-usable.** Files are self-contained markdown. No database, no build step.
2. **Diffable.** Plain markdown with short lines so a rate change is a one-line diff.
3. **Honest about gaps.** `needs-verification` is a first-class state, not a failure.
4. **Portable.** A skill folder can be lifted out and used alone.
