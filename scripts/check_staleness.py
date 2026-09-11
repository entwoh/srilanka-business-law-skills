#!/usr/bin/env python3
import argparse
import datetime as dt
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent

FAST_MOVING = {"tax-compliance": 90, "employment-law": 120}


def load_meta(path: pathlib.Path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    return yaml.safe_load(parts[1]) if len(parts) >= 3 else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=180, help="default staleness window")
    args = ap.parse_args()

    today = dt.date.today()
    stale: list[tuple[int, str, int]] = []

    for path in sorted((ROOT / "skills").rglob("*.md")):
        if path.name == "SKILL.md":
            continue
        meta = load_meta(path)
        if not meta or "last_verified" not in meta:
            continue

        verified = meta["last_verified"]
        if isinstance(verified, str):
            try:
                verified = dt.date.fromisoformat(verified)
            except ValueError:
                continue

        rel = path.relative_to(ROOT)
        window = args.days
        for domain, override in FAST_MOVING.items():
            if domain in str(rel):
                window = override

        age = (today - verified).days
        if age > window:
            stale.append((age, str(rel), window))

    if not stale:
        print("Nothing stale.")
        return 0

    print(f"{len(stale)} file(s) need re-verification:\n")
    for age, rel, window in sorted(stale, reverse=True):
        print(f"  {age:>4}d (limit {window}d)  {rel}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
