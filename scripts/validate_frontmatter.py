#!/usr/bin/env python3
"""Validate the minimal metadata contract for repository skills."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
FRONTMATTER = re.compile(r"\A---\n(?P<body>.*?)\n---\n", re.DOTALL)
FIELD = re.compile(r"^(name|description):\s*(.+)$", re.MULTILINE)
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def main() -> int:
    errors: list[str] = []
    skill_files = sorted(SKILLS.glob("*/SKILL.md"))
    if len(skill_files) != 10:
        errors.append(f"expected exactly 10 skills; found {len(skill_files)}")

    for path in skill_files:
        text = path.read_text(encoding="utf-8")
        match = FRONTMATTER.match(text)
        if not match:
            errors.append(f"{path.relative_to(ROOT)}: missing YAML frontmatter")
            continue
        fields = dict(FIELD.findall(match.group("body")))
        if set(fields) != {"name", "description"}:
            errors.append(f"{path.relative_to(ROOT)}: requires name and description only")
        if not NAME.fullmatch(fields.get("name", "")):
            errors.append(f"{path.relative_to(ROOT)}: invalid name")
        if fields.get("name") != path.parent.name:
            errors.append(f"{path.relative_to(ROOT)}: name must match directory")
        if len(fields.get("description", "")) < 30:
            errors.append(f"{path.relative_to(ROOT)}: description is too short")
        if not (path.parent / "references").is_dir():
            errors.append(f"{path.relative_to(ROOT)}: references directory is required")

    if errors:
        print("Validation failed:", *[f"- {error}" for error in errors], sep="\n")
        return 1
    print(f"Validated {len(skill_files)} skills.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
