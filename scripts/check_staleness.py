#!/usr/bin/env python3
"""Fail when dated legal-reference material is more than one year old."""

from datetime import date, datetime
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DATE_LINE = re.compile(
    r"^(?:Last verified:\s*|last_verified:\s*)(\d{4}-\d{2}-\d{2})\s*$",
    re.MULTILINE,
)
MAX_AGE_DAYS = 365


def main() -> int:
    candidates = list((ROOT / "shared").glob("*.md")) + list(
        (ROOT / "skills").glob("*/references/*.md")
    )
    errors: list[str] = []
    today = date.today()
    for path in sorted(candidates):
        match = DATE_LINE.search(path.read_text(encoding="utf-8"))
        relative = path.relative_to(ROOT)
        if not match:
            errors.append(f"{relative}: missing Last verified date")
            continue
        verified = datetime.strptime(match.group(1), "%Y-%m-%d").date()
        if verified > today:
            errors.append(f"{relative}: verification date is in the future")
        elif (today - verified).days > MAX_AGE_DAYS:
            errors.append(f"{relative}: verification is older than {MAX_AGE_DAYS} days")

    if errors:
        print("Staleness check failed:", *[f"- {error}" for error in errors], sep="\n")
        return 1
    print(f"Checked {len(candidates)} dated references.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
