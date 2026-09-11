# Sri Lanka Business Law Skills

An open, community-maintained knowledge base covering Sri Lankan business law —
company formation, secretarial compliance, share transactions, employment, tax, contracts,
foreign investment, IP, data protection and dispute resolution.

Sri Lankan legal information online is scattered, often years out of date, and frequently
wrong on the details that matter (rates, thresholds, form numbers, commencement dates).
This repository is an attempt to fix that: a citation-disciplined, version-controlled,
openly reviewable knowledge base.

> **This is not legal advice.** See [DISCLAIMER.md](DISCLAIMER.md). Everything here is a
> research aid. Statutory interpretation, advice and appearance before courts and tribunals
> in Sri Lanka are reserved to Attorneys-at-Law.

---

## What's in here

| Skill | Covers |
|---|---|
| [`sl-company-formation`](skills/company-formation/) | Entity choice, name approval, eROC incorporation, post-incorporation setup |
| [`sl-company-secretarial`](skills/company-secretarial/) | Annual return, meetings, resolutions, registers, **beneficial ownership**, directors' duties |
| [`sl-shares-and-capital`](skills/shares-and-capital/) | Share issues, transfers, buy-backs, solvency test, shareholder agreements |
| [`sl-employment-law`](skills/employment-law/) | Contracts, wages and hours, EPF/ETF/gratuity, termination, TEWA, Labour Tribunals |
| [`sl-tax-compliance`](skills/tax-compliance/) | Corporate income tax, VAT, SSCL, WHT/AIT, APIT, filing calendar |
| [`sl-commercial-contracts`](skills/commercial-contracts/) | Formation, drafting, stamp duty, execution, remedies |
| [`sl-foreign-investment`](skills/foreign-investment/) | BOI, sectoral restrictions, exchange control, IIA accounts, land |
| [`sl-intellectual-property`](skills/intellectual-property/) | Trade marks, copyright, designs, patents, enforcement |
| [`sl-data-protection`](skills/data-protection/) | PDPA obligations and phased commencement, electronic transactions |
| [`sl-dispute-resolution`](skills/dispute-resolution/) | Courts and jurisdiction, debt recovery, arbitration |

Shared, cross-cutting material lives in [`shared/`](shared/): a statute index, a regulator
index, the **complete ROC forms list**, and a glossary.

---

## Quick start

```bash
git clone https://github.com/<your-org>/srilanka-business-law-skills.git
```

Each topic is a self-contained directory with an entry-point file and `references/` files.
Just read the markdown — every reference file is written to be usable on its own, with
section references to the governing statute and links to the primary source.

---

## The verification rule

Every reference file carries frontmatter like this:

```yaml
last_verified: 2026-09-11
verification_status: verified      # verified | partial | needs-verification
primary_sources:
  - "Companies Act No. 7 of 2007, s 58"
  - "https://drc.gov.lk/en/?page_id=1998"
```

- **verified** — checked against a primary source (statute text, gazette, regulator site) on the date shown.
- **partial** — core position verified; some figures or procedural detail taken from secondary sources.
- **needs-verification** — drafted from general knowledge. Treat as a starting point only.

Content with `needs-verification` is still merged, because an honestly-labelled draft is more
useful than a gap. It is not presented as settled law.

### Why this matters — two real examples

**1. The VAT threshold that wasn't.** The 2026 Budget proposed cutting the VAT registration
threshold from LKR 60m to LKR 36m. Several professional firms published client alerts saying
it took effect 1 July 2026. **The cut was dropped before enactment** — the VAT (Amendment)
Act No. 14 of 2026 kept the threshold at LKR 60m. A skill that scraped the client alerts
would have told a business to register when it did not have to.

**2. The 40% rate that became 45%.** Betting, gaming, liquor and tobacco moved from 40% to
45% with effect from 1 April 2025 under the Inland Revenue (Amendment) Act No. 2 of 2025.
Plenty of guides still say 40%.

Proposals are not law. Bills are not Acts. Acts are not in force until commenced.
See [docs/verification-policy.md](docs/verification-policy.md).

---

## Contributing

Corrections are the single most valuable contribution. If a rate, threshold, form number or
date here is wrong, please open an issue using the **Legal accuracy** template — even if you
can't fix it yourself.

Read [CONTRIBUTING.md](CONTRIBUTING.md) for the citation format, the review process, and
what we will and won't accept.

Sri Lankan law changes fast. The repository aims for a quarterly sweep of the tax and labour
files, and an immediate patch when a commencement gazette lands.

---

## Licence

- **Content** (all `.md` files): [CC BY 4.0](LICENSE-CONTENT.md) — use it, adapt it, credit it.
- **Code** (scripts, workflows): [MIT](LICENSE).

Sri Lankan statutes are Crown material published by the Government Printer; this project
reproduces only short quotations, section references and links, not full statutory text.