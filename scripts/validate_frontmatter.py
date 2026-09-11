#!/usr/bin/env python3
"""Validate frontmatter on every skill and reference file.

Enforces the rules in docs/verification-policy.md:
  - required keys present
  - verification_status is one of the allowed values
  - last_verified parses as a date and is not in the future
  - needs-verification files carry the warning banner
"""
import datetime as dt
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
ALLOWED_STATUS = {"verified", "partial", "needs-verification"}
BANNER = "Unverified draft"
REQUIRED = {"title", "last_verified", "verification_status"}

errors: list[str] = []


def split_frontmatter(text: str):
    if not text.startswith("---"):
        return None, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, text
    return yaml.safe_load(parts[1]), parts[2]


def check(path: pathlib.Path) -> None:
    rel = path.relative_to(ROOT)
    meta, body = split_frontmatter(path.read_text(encoding="utf-8"))

    if meta is None:
        errors.append(f"{rel}: missing YAML frontmatter")
        return

    if path.name == "SKILL.md":
        for key in ("name", "description"):
            if not meta.get(key):
                errors.append(f"{rel}: SKILL.md requires '{key}'")
        return

    missing = REQUIRED - set(meta)
    if missing:
        errors.append(f"{rel}: missing key(s) {sorted(missing)}")

    status = meta.get("verification_status")
    if status not in ALLOWED_STATUS:
        errors.append(f"{rel}: verification_status '{status}' not in {sorted(ALLOWED_STATUS)}")

    verified = meta.get("last_verified")
    if isinstance(verified, str):
        try:
            verified = dt.date.fromisoformat(verified)
        except ValueError:
            errors.append(f"{rel}: last_verified '{verified}' is not YYYY-MM-DD")
            verified = None
    if isinstance(verified, dt.date) and verified > dt.date.today():
        errors.append(f"{rel}: last_verified {verified} is in the future")

    if status == "verified" and not meta.get("primary_sources"):
        errors.append(f"{rel}: marked 'verified' but lists no primary_sources")

    if status == "needs-verification" and BANNER not in body:
        errors.append(f"{rel}: needs-verification but missing the '{BANNER}' banner")


def main() -> int:
    for path in sorted((ROOT / "skills").rglob("*.md")):
        check(path)

    if errors:
        print("Frontmatter validation failed:\n")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("Frontmatter OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
