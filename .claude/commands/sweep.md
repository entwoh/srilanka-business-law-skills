---
description: Run the scheduled re-verification sweep across a domain
---

Run the re-verification sweep for: $ARGUMENTS (e.g. `tax-compliance`, or `all`).

1. `python scripts/check_staleness.py` to see what is overdue. Tax files have a 90-day window,
   employment 120, everything else 180.
2. For each stale file, follow the `/verify` process.
3. Check the maintenance calendar in CHANGELOG.md for anything keyed to the current date —
   1 April rate changes, 1 January labour figures, November budget proposals.
4. Update `shared/statutes-index.md` if any statute's status changed.
5. Summarise: what changed, what is now stale but unchecked, what needs a human lawyer.

Do not mark anything `verified` that you did not check this session.
