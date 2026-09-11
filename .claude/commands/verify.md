---
description: Verify one reference file against primary sources and update its frontmatter
---

Verify the file at $ARGUMENTS against primary sources.

1. Read the file and list every factual claim: rates, thresholds, dates, form numbers,
   section references, deadlines.
2. For each, find a **tier 1 or tier 2** source (statute text, gazette, or the regulator's own
   site — drc.gov.lk, ird.gov.lk, dpa.gov.lk, cbsl.gov.lk). Firm alerts and EOR guides do not
   count. Check the four commencement questions in docs/verification-policy.md.
3. Correct anything wrong. Add the effective date to any figure missing one.
4. Where sources conflict and you cannot resolve it against a primary source, add a
   ⚠️ conflict note rather than picking a side.
5. Update frontmatter:
   - `verified` only if you checked **every** material claim against tier 1 or 2
   - `partial` if you checked some — say inline which you did not
   - leave `needs-verification` (and its ⚠️ banner) if you could not check the core claims
   - set `last_verified` to today only if you actually verified today
   - add each source to `primary_sources`
6. Run `python scripts/validate_frontmatter.py`.
7. Add a CHANGELOG entry under the right marker if the legal position changed.

Report what you checked, what you could not, and anything that turned out to be wrong.
