#!/usr/bin/env python3
"""Token / structure audit of the skills and shared layer.

Stdlib only. Read-only over content: writes a Markdown report and a JSON snapshot.

    python scripts/audit_tokens.py                       # -> docs/audit-baseline.md (+ .json)
    python scripts/audit_tokens.py --out docs/audit-after.md

A block between <!-- manual:start --> and <!-- manual:end --> in an existing report is
preserved on regeneration, so hand-written analysis survives re-runs.
"""
import argparse
import collections
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCAN_DIRS = ("skills", "shared")

LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")
BACKTICK_PATH_RE = re.compile(r"`((?:\.\./)+[\w./-]+\.md)`(?!\]\()")
MANUAL_RE = re.compile(r"<!-- manual:start -->.*?<!-- manual:end -->", re.S)

STATUTE_RE = re.compile(
    r"((?:(?:[A-Z][\w'’&-]*|of|and|the|for|on|to|in|\([^)]{1,60}\))\s+){1,16}?"
    r"(?:Act|Ordinance|Law|Regulation|Code|Bill)"
    r",?\s+No\.?\s*\d+[A-Z]?\s+of\s+\d{4})"
)
FORM_RE = re.compile(r"\b(?:Form|F)\s?(BO\s?\d+|\d{1,2}[A-C]?)\b(?:\s*/\s*(\d{1,2}[A-C]?))?")
REGULATORS = {
    "ROC / DRC": r"\bROC\b|\bDRC\b|Registrar of Companies|Registrar\b",
    "eROC": r"\beROC\b",
    "IRD": r"\bIRD\b|Inland Revenue Department|Commissioner-General of Inland Revenue",
    "CBSL": r"\bCBSL\b|Central Bank",
    "BOI": r"\bBOI\b|Board of Investment",
    "NIPO": r"\bNIPO\b|National Intellectual Property Office",
    "SEC": r"\bSEC\b|Securities and Exchange Commission",
    "CSE": r"\bCSE\b|Colombo Stock Exchange",
    "DPA": r"\bDPA\b|Data Protection Authority",
    "CAA": r"\bCAA\b|Consumer Affairs Authority",
    "Department of Labour": r"Department of Labour|Labour Department|Commissioner(?:-General)? of Labour",
    "ETF Board": r"\bETFB\b|Employees' Trust Fund Board",
    "Labour Tribunal": r"Labour Tribunal",
    "Commercial High Court": r"Commercial High Court",
    "FIU": r"Financial Intelligence Unit|\bFIU\b",
    "Port City Commission": r"Port City|Colombo Port City Economic Commission",
    "Provincial Registrar of Business Names": r"Registrar of Business Names|Business Names registration",
}
DEADLINE_RE = re.compile(
    r"(within\s+\d+\s+(?:working\s+)?(?:days?|months?|years?|weeks?)"
    r"|\b\d+\s+(?:working\s+)?(?:days?|months?)\s+(?:of|from|after|before|following)\b"
    r"|\bby\s+(?:the\s+)?\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)"
    r"|\b(?:on or before|no later than|due (?:on|by))\b[^.;|]{0,40}"
    r"|\b(?:annually|monthly|quarterly)\b(?![\s-]+(?:earnings|terminal|salary|paid|rated|filing))(?!-rated))",
    re.I,
)


def rel(p: pathlib.Path) -> str:
    return p.relative_to(ROOT).as_posix()


def approx_tokens(text: str) -> int:
    return round(len(text) / 4)


def split_frontmatter(text: str):
    if not text.startswith("---"):
        return "", text, 0
    end = text.find("\n---", 3)
    if end < 0:
        return "", text, 0
    fm = text[3:end]
    body_start = end + 4
    return fm, text[body_start:], text[:body_start].count("\n")


def fm_value(fm: str, key: str) -> str:
    """Tiny YAML subset: scalar, quoted scalar, or folded/literal block."""
    lines = fm.splitlines()
    for i, line in enumerate(lines):
        m = re.match(rf"^{key}:\s*(.*)$", line)
        if not m:
            continue
        val = m.group(1).strip()
        if val in (">", "|", ">-", "|-"):
            block = []
            for nxt in lines[i + 1:]:
                if nxt.strip() and not nxt.startswith((" ", "\t")):
                    break
                block.append(nxt.strip())
            return " ".join(b for b in block if b)
        return val.strip("'\"")
    return ""


def iter_files():
    for d in SCAN_DIRS:
        yield from sorted((ROOT / d).rglob("*.md"))


def skill_of(path: pathlib.Path):
    parts = path.relative_to(ROOT).parts
    return parts[1] if parts[0] == "skills" and len(parts) > 2 else None


# ---------------------------------------------------------------- metrics


def file_metrics(path: pathlib.Path):
    text = path.read_text(encoding="utf-8")
    fm, body, _ = split_frontmatter(text)
    links = [m.group(1) for m in LINK_RE.finditer(text)]
    code_paths = [m.group(1) for m in BACKTICK_PATH_RE.finditer(text)]
    info = {
        "file": rel(path),
        "skill": skill_of(path),
        "lines": text.count("\n") + (0 if text.endswith("\n") else 1),
        "chars": len(text),
        "tokens": approx_tokens(text),
        "h2": len(re.findall(r"^## ", text, re.M)),
        "h3": len(re.findall(r"^### ", text, re.M)),
        "links": links,
        "code_paths": code_paths,
    }
    if path.name == "SKILL.md":
        desc = fm_value(fm, "description")
        name = fm_value(fm, "name")
        info.update(
            name=name,
            description=desc,
            desc_chars=len(desc),
            desc_words=len(desc.split()),
            always_loaded_tokens=approx_tokens(f"name: {name}\ndescription: {desc}"),
            body_lines=body.strip("\n").count("\n") + 1 if body.strip() else 0,
        )
    return info


# ------------------------------------------------------------ duplication


def norm(s: str) -> str:
    s = re.sub(r"[*_`>#|]", " ", s.lower())
    s = re.sub(r"[^\w\s%]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def paragraphs(text: str):
    _, body, offset = split_frontmatter(text)
    line_no = offset + 1
    buf, start = [], None
    for line in body.split("\n"):
        if line.strip() and not line.lstrip().startswith(("#", "|", "```")):
            if start is None:
                start = line_no
            buf.append(line)
        else:
            if buf:
                yield start, " ".join(buf)
            buf, start = [], None
        line_no += 1
    if buf:
        yield start, " ".join(buf)


def sentences(text: str):
    for start, para in paragraphs(text):
        for s in re.split(r"(?<=[.!?])\s+(?=[A-Z*])|^\s*[-*]\s+|\s+-\s+(?=\*\*)", para):
            s = s.strip(" -*")
            if len(norm(s).split()) >= 7:
                yield start, s


def shingles(words, k=3):
    return {" ".join(words[i:i + k]) for i in range(max(1, len(words) - k + 1))}


def find_duplication(files):
    para_index = collections.defaultdict(list)
    sent_items = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        for line, para in paragraphs(text):
            n = norm(para)
            if len(n.split()) >= 8:
                para_index[n].append((rel(path), line, para))
        for line, s in sentences(text):
            words = norm(s).split()
            sent_items.append((rel(path), line, s, shingles(words)))

    exact_paras = [v for v in para_index.values() if len({f for f, _, _ in v}) > 1]

    inverted = collections.defaultdict(set)
    for i, (_, _, _, sh) in enumerate(sent_items):
        for g in sh:
            inverted[g].add(i)
    pairs = {}
    for i, (fi, li, si, shi) in enumerate(sent_items):
        cand = collections.Counter()
        for g in shi:
            for j in inverted[g]:
                if j > i:
                    cand[j] += 1
        for j, overlap in cand.items():
            fj, lj, sj, shj = sent_items[j]
            if fj == fi:
                continue
            jac = overlap / len(shi | shj)
            if jac >= 0.6:
                pairs[(i, j)] = jac
    # group near-duplicate sentences into clusters
    parent = {}

    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i, j in pairs:
        parent[find(i)] = find(j)
    clusters = collections.defaultdict(list)
    for i, j in pairs:
        clusters[find(i)].extend([i, j])
    groups = []
    for members in clusters.values():
        uniq = sorted(set(members))
        items = [(sent_items[k][0], sent_items[k][1], sent_items[k][2]) for k in uniq]
        best = max(pairs.get((a, b), 0) for a in uniq for b in uniq if a < b and (a, b) in pairs)
        groups.append({"similarity": round(best, 2), "items": items})
    groups.sort(key=lambda g: (-len(g["items"]), -g["similarity"]))
    return exact_paras, groups


# ---------------------------------------------------------- cross-refs


def cross_refs(metrics):
    edges, broken, escapes = [], [], []
    for m in metrics:
        src = ROOT / m["file"]
        for target in m["links"] + m["code_paths"]:
            if re.match(r"^[a-z]+:", target) or target.startswith("#"):
                continue
            path_part = target.split("#", 1)[0]
            resolved = (src.parent / path_part).resolve()
            try:
                tgt_rel = resolved.relative_to(ROOT).as_posix()
            except ValueError:
                tgt_rel = str(resolved)
            kind = "link" if target in m["links"] else "code-path"
            edges.append((m["file"], tgt_rel, kind))
            if not resolved.exists():
                broken.append((m["file"], target, kind))
            if m["skill"]:
                skill_root = (ROOT / "skills" / m["skill"]).resolve()
                if skill_root not in resolved.parents and resolved != skill_root:
                    escapes.append((m["file"], target, kind, "shared" in path_part))
    return edges, broken, escapes


# ---------------------------------------------------------- entities


def entity_mentions(files):
    statutes = collections.defaultdict(list)
    forms = collections.defaultdict(list)
    regs = collections.defaultdict(list)
    deadlines = []
    reg_res = {k: re.compile(v) for k, v in REGULATORS.items()}
    for path in files:
        r = rel(path)
        for n, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
            if n <= 12 and line.startswith(("  - ", "primary_sources", "title:")):
                pass  # frontmatter mentions still count as mentions
            for m in STATUTE_RE.finditer(line):
                name = re.sub(r"^(?:(?:The|the|and|of|under|by|to|in|for|on)\s+)+", "", m.group(1).strip())
                name = re.sub(r"\s+", " ", name)
                key = re.sub(r",?\s+No\.?\s*", " No. ", name)
                statutes[key].append(f"{r}:{n}")
            for m in FORM_RE.finditer(line):
                forms[f"Form {m.group(1).replace(' ', ' ')}"].append(f"{r}:{n}")
                if m.group(2):
                    forms[f"Form {m.group(2)}"].append(f"{r}:{n}")
            for name, rx in reg_res.items():
                if rx.search(line):
                    regs[name].append(f"{r}:{n}")
            phrases = dict.fromkeys(m.group(0).strip().lower() for m in DEADLINE_RE.finditer(line))
            if phrases:
                deadlines.append((f"{r}:{n}", "; ".join(phrases), line.strip()))
    return statutes, forms, regs, deadlines


# -------------------------------------------------------------- report


def fmt_locs(locs, limit=6):
    shown = ", ".join(locs[:limit])
    return shown + (f" … (+{len(locs) - limit})" if len(locs) > limit else "")


def build(out: pathlib.Path):
    files = list(iter_files())
    metrics = [file_metrics(p) for p in files]
    by_skill = collections.defaultdict(list)
    for m in metrics:
        if m["skill"]:
            by_skill[m["skill"]].append(m)

    skills_summary = []
    for skill, ms in sorted(by_skill.items()):
        sk = next(m for m in ms if m["file"].endswith("SKILL.md"))
        refs = [m for m in ms if "/references/" in m["file"]]
        largest = max(refs, key=lambda m: m["tokens"]) if refs else None
        skills_summary.append({
            "skill": skill,
            "name": sk["name"],
            "desc_chars": sk["desc_chars"],
            "desc_words": sk["desc_words"],
            "always_loaded_tokens": sk["always_loaded_tokens"],
            "skill_md_tokens": sk["tokens"],
            "skill_md_lines": sk["lines"],
            "refs": len(refs),
            "refs_tokens": sum(m["tokens"] for m in refs),
            "largest_ref": largest["file"].split("/")[-1] if largest else "-",
            "typical_load": sk["tokens"] + (largest["tokens"] if largest else 0),
            "full_load": sk["tokens"] + sum(m["tokens"] for m in refs),
            "avg_ref_tokens": round(sum(m["tokens"] for m in refs) / len(refs)) if refs else 0,
        })

    exact_paras, near_groups = find_duplication(files)
    xedges, broken, escapes = cross_refs(metrics)
    statutes, forms, regs, deadlines = entity_mentions(files)

    total_tokens = sum(m["tokens"] for m in metrics)
    always = sum(s["always_loaded_tokens"] for s in skills_summary)
    dup_tokens = sum(
        approx_tokens(g["items"][0][2]) * (len(g["items"]) - 1) for g in near_groups
    )

    L = []
    w = L.append
    w("# Token & structure audit\n")
    w(f"Generated by `scripts/audit_tokens.py`. Token counts are approximate (chars / 4). "
      f"Scope: every `.md` under {', '.join(f'`{d}/`' for d in SCAN_DIRS)}.\n")
    w("## Totals\n")
    w("| Metric | Value |\n|---|---|")
    w(f"| Files scanned | {len(metrics)} |")
    w(f"| Total tokens (all files) | {total_tokens:,} |")
    w(f"| **Always-loaded tokens** (10 × name + description) | **{always:,}** |")
    w(f"| Mean typical load (SKILL.md + largest reference) | "
      f"{round(sum(s['typical_load'] for s in skills_summary) / len(skills_summary)):,} |")
    w(f"| Mean full-skill load (SKILL.md + all references) | "
      f"{round(sum(s['full_load'] for s in skills_summary) / len(skills_summary)):,} |")
    w(f"| Shared layer tokens | {sum(m['tokens'] for m in metrics if m['file'].startswith('shared/')):,} |")
    w(f"| Near-duplicate sentence groups across files | {len(near_groups)} (≈{dup_tokens:,} redundant tokens) |")
    w(f"| Exact duplicate paragraphs across files | {len(exact_paras)} |")
    w(f"| Broken links | {len(broken)} |")
    w(f"| Links escaping their skill folder | {len(escapes)} |")
    w("")

    w("## Per skill\n")
    w("| Skill | Desc chars | Desc words | Always-loaded tok | SKILL.md lines | SKILL.md tok | Refs | "
      "Refs tok | Largest ref | Typical load | Full load |")
    w("|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|")
    for s in skills_summary:
        w(f"| {s['skill']} | {s['desc_chars']} | {s['desc_words']} | {s['always_loaded_tokens']} | "
          f"{s['skill_md_lines']} | {s['skill_md_tokens']} | {s['refs']} | {s['refs_tokens']:,} | "
          f"{s['largest_ref']} | {s['typical_load']:,} | {s['full_load']:,} |")
    w("")

    w("## Per file\n")
    w("| File | Lines | Chars | ~Tokens | H2 | H3 | Links |")
    w("|---|---:|---:|---:|---:|---:|---:|")
    for m in metrics:
        w(f"| `{m['file']}` | {m['lines']} | {m['chars']:,} | {m['tokens']:,} | {m['h2']} | "
          f"{m['h3']} | {len(m['links']) + len(m['code_paths'])} |")
    w("")

    w("## Duplication\n")
    w("### Exact duplicate paragraphs (normalised) in more than one file\n")
    if exact_paras:
        for v in exact_paras:
            w(f"- “{v[0][2][:140]}…” — " + ", ".join(f"`{f}:{l}`" for f, l, _ in v))
    else:
        w("None found.")
    w("")
    w("### Near-identical sentences across files (3-gram Jaccard ≥ 0.6)\n")
    if near_groups:
        for g in near_groups:
            w(f"- **sim {g['similarity']}** — " + "; ".join(
                f"`{f}:{l}` “{s[:110]}{'…' if len(s) > 110 else ''}”" for f, l, s in g["items"]))
    else:
        w("None found.")
    w("")

    w("## Cross-reference map\n")
    w("### File → linked files\n")
    grouped = collections.defaultdict(set)
    for s, t, _ in xedges:
        grouped[s].add(t)
    w("| From | To |\n|---|---|")
    for s in sorted(grouped):
        w(f"| `{s}` | " + "<br>".join(f"`{t}`" for t in sorted(grouped[s])) + " |")
    w("")
    w("### Broken links\n")
    if broken:
        for f, t, k in broken:
            w(f"- `{f}` → `{t}` ({k})")
    else:
        w("None.")
    w("")
    w("### Links that leave the skill folder (break after single-skill install)\n")
    w("Includes backtick-quoted relative paths, which Claude follows like links. "
      "`../../shared` references are marked **shared**.\n")
    if escapes:
        for f, t, k, sh in escapes:
            w(f"- `{f}` → `{t}` ({k}){' — **shared**' if sh else ''}")
    else:
        w("None.")
    w("")

    w("## Entity mentions (candidates for canonical nodes)\n")
    w("### Statutes and instruments\n")
    w("| Mention (normalised) | Count | Locations |\n|---|---:|---|")
    for k in sorted(statutes, key=lambda k: (-len(statutes[k]), k)):
        w(f"| {k} | {len(statutes[k])} | {fmt_locs(statutes[k])} |")
    w("")
    w("### Regulators and bodies\n")
    w("| Regulator | Count | Locations |\n|---|---:|---|")
    for k in sorted(regs, key=lambda k: -len(regs[k])):
        w(f"| {k} | {len(regs[k])} | {fmt_locs(regs[k])} |")
    w("")
    w("### ROC forms\n")
    w("| Form | Count | Locations |\n|---|---:|---|")

    def form_key(k):
        m = re.match(r"Form (BO ?)?(\d+)([A-C]?)", k)
        return (1 if m and m.group(1) else 0, int(m.group(2)) if m else 999, m.group(3) if m else k)

    for k in sorted(forms, key=form_key):
        w(f"| {k} | {len(forms[k])} | {fmt_locs(forms[k])} |")
    w("")
    w("### Deadlines and time limits\n")
    w("| Location | Phrase | Line |\n|---|---|---|")
    for loc, phrase, line in deadlines:
        w(f"| `{loc}` | {phrase} | {line[:120].replace('|', '/')} |")
    w("")

    manual_default = (
        "<!-- manual:start -->\n## Top 10 token-saving opportunities\n\n"
        "_Write the analysis here; this block is preserved on regeneration._\n<!-- manual:end -->"
    )
    manual = manual_default
    if out.exists():
        m = MANUAL_RE.search(out.read_text(encoding="utf-8"))
        if m:
            manual = m.group(0)
    w(manual)
    w("")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")

    snapshot = {
        "totals": {
            "files": len(metrics),
            "tokens": total_tokens,
            "always_loaded_tokens": always,
            "near_duplicate_groups": len(near_groups),
            "near_duplicate_tokens": dup_tokens,
            "broken_links": len(broken),
            "escaping_links": len(escapes),
        },
        "skills": skills_summary,
        "files": [{k: v for k, v in m.items() if k not in ("links", "code_paths", "description")}
                  for m in metrics],
    }
    out.with_suffix(".json").write_text(json.dumps(snapshot, indent=1), encoding="utf-8")
    print(f"wrote {rel(out)} and {rel(out.with_suffix('.json'))}: {len(metrics)} files, "
          f"{total_tokens:,} tokens, always-loaded {always}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default="docs/audit-baseline.md")
    args = ap.parse_args()
    return build(ROOT / args.out)


if __name__ == "__main__":
    sys.exit(main())
