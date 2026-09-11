# Architecture

`skills/` contains task entry points. Each skill routes a request to its local `references/` material and shared indexes. `shared/` holds cross-cutting lookup material; it must not duplicate a skill's workflow guidance. `scripts/` enforce repository-wide metadata expectations. GitHub automation runs those checks for every change.

```text
request → skills/<domain>/SKILL.md → local references + shared indexes → verified primary source
```

Skills provide process, not definitive legal outcomes. Shared indexes identify authorities and official destinations; they are curated aids, not substitutes for source verification.
