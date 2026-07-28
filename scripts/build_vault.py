"""
build_vault.py
Generates this project's Obsidian vault from its YAML ontology.

Output: ../vault/
  ├── .obsidian/                 (settings — never touched by this script)
  ├── CLAUDE.md
  ├── <PROJECT_NAME>.md          (index note)
  ├── Papers/
  ├── Topics/
  └── Researchers/

Run: python scripts/build_vault.py

NOTE: korea-policy-papers/scripts/build_vault.py is the twin of this file.
The two differ only in the PROJECT_NAME / VAULT_BLURB constants below — fix
both together, or they drift.
"""

import os, re, yaml
from collections import defaultdict

HERE     = os.path.dirname(os.path.abspath(__file__))
ROOT     = os.path.abspath(os.path.join(HERE, ".."))
ONTOLOGY = os.path.join(ROOT, "data", "ontology")
VAULT    = os.path.join(ROOT, "vault")

PROJECT_NAME = "Behavioral Public Economics"

VAULT_BLURB = """\
Papers from Bernheim & Taubinsky (2018) "Behavioral Public Economics"
(NBER WP 24828) plus the NBER Behavioral Public Economics Boot Camp
reading list — welfare analysis, corrective taxation, nudges, insurance,
household finance, behavioral IO, and mobility.
"""


# ── helpers ──────────────────────────────────────────────────────────────────

def slug(s):
    """Clean a string for use as an Obsidian filename (no path separators)."""
    s = str(s)
    s = s.replace("/", "-").replace("\\", "-").replace(":", " ")
    s = re.sub(r'[<>"|?*]', '', s)
    return s.strip()

def paper_fname(p):
    """Card & Krueger 1994  /  Chetty et al. 2014

    Base name only — NOT unique on its own. Two papers sharing a first author
    and a year collapse onto the same string. Always go through
    assign_paper_fnames() to get the disambiguated name.
    """
    authors = p.get("authors", [])
    if not authors:
        return slug(p["id"])
    if len(authors) == 1:
        names = authors[0]
    elif len(authors) == 2:
        names = f"{authors[0]} & {authors[1]}"
    else:
        names = f"{authors[0]} et al."
    return slug(f"{names} {p.get('year','')}")

def disambiguator(i):
    """0 → 'a', 1 → 'b', … 25 → 'z', then '-27', '-28', … as a safety valve."""
    return chr(ord("a") + i) if i < 26 else f"-{i + 1}"

def assign_paper_fnames(papers):
    """paper id → unique note filename.

    Collisions get an APA-style letter appended to the year: "Allcott et al.
    2018a" / "Allcott et al. 2018b". The letter is assigned in title order, not
    in file order, so re-sorting papers.yaml does not reshuffle filenames and
    break wikilinks that already point at them.

    Returns (mapping, renamed).
    """
    groups = defaultdict(list)
    for p in papers:
        groups[paper_fname(p)].append(p)

    mapping, renamed = {}, []
    for base, members in groups.items():
        if len(members) == 1:
            mapping[members[0]["id"]] = base
            continue

        for i, p in enumerate(sorted(members, key=lambda x: (x.get("title", ""), x["id"]))):
            if not p.get("authors"):          # id-based name, already unique
                mapping[p["id"]] = base
                continue
            name = slug(f"{base}{disambiguator(i)}")
            mapping[p["id"]] = name
            renamed.append((base, name, p["id"]))
    return mapping, renamed

def check_unique(kind, id_to_fname):
    """Abort loudly rather than let one note silently overwrite another.

    Papers are disambiguated automatically; researchers and topics are not,
    because a duplicate there means the ontology has two entries for one
    entity — a data problem to fix by hand, not to paper over with a suffix.
    """
    by_fname = defaultdict(list)
    for id_, fname in id_to_fname.items():
        by_fname[fname].append(id_)

    clashes = {f: ids for f, ids in by_fname.items() if len(ids) > 1}
    if clashes:
        detail = "\n".join(f"    {f!r} ← {', '.join(sorted(ids))}" for f, ids in sorted(clashes.items()))
        raise SystemExit(
            f"\n[{kind}] duplicate note filenames — these would overwrite each other:\n"
            f"{detail}\n"
            f"Give the colliding entries distinct labels/names in the ontology YAML."
        )

GENERATED_TYPES = ("paper", "topic", "subtopic", "researcher")

def prune_stale(folders, created):
    """Delete generated notes this run no longer produces.

    Renaming a note (e.g. "Chetty et al. 2014" → "…2014a") writes the new file
    but leaves the old one behind, where it lingers as an orphan node in the
    graph view. Only files carrying generator frontmatter are removed, so a
    hand-written note dropped into these folders survives.
    """
    keep = {os.path.normcase(os.path.abspath(p)) for p in created}
    removed = []

    for folder in folders:
        if not os.path.isdir(folder):
            continue
        for fname in sorted(os.listdir(folder)):
            path = os.path.join(folder, fname)
            if not fname.endswith(".md") or not os.path.isfile(path):
                continue
            if os.path.normcase(os.path.abspath(path)) in keep:
                continue
            with open(path, encoding="utf-8") as f:
                head = f.read(200)
            if not re.match(r"---\s*\ntype:\s*(%s)\b" % "|".join(GENERATED_TYPES), head):
                print(f"    kept (not generator output): {fname}")
                continue
            os.remove(path)
            removed.append(fname)
    return removed

def researcher_fname(r):
    return slug(r["name"])

def topic_fname(t):
    label = t.get("label_en") or t.get("label", t["id"])
    return slug(label)

def subtopic_fname(s):
    label = s.get("label_en") or s.get("label", s["id"])
    return slug(label)

def wikilink(fname):
    return f"[[{fname}]]"

_written_paths = set()

def write(path, content):
    """Write a note, refusing to clobber one written earlier in the same run.

    Last-resort guard behind check_unique(): filenames are case-insensitive on
    Windows, so "Chetty 2014" and "chetty 2014" are the same file even though
    the uniqueness check above sees two distinct strings.
    """
    key = os.path.normcase(os.path.abspath(path))
    if key in _written_paths:
        raise SystemExit(f"\n[write] {path} written twice in one run — notes would be lost.")
    _written_paths.add(key)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path

def load(filename):
    with open(os.path.join(ONTOLOGY, filename), encoding="utf-8") as f:
        return yaml.safe_load(f)


# ── core builder ─────────────────────────────────────────────────────────────

def build():
    topics_data      = load("topics.yaml")
    papers_data      = load("papers.yaml")
    researchers_data = load("researchers.yaml")

    papers      = papers_data["papers"]
    researchers = researchers_data["researchers"]
    topics_raw  = topics_data["topics"]

    pap_dir = os.path.join(VAULT, "Papers")
    top_dir = os.path.join(VAULT, "Topics")
    res_dir = os.path.join(VAULT, "Researchers")

    # ── index maps ──────────────────────────────────────────────────────────

    paper_id_to_fname, renamed = assign_paper_fnames(papers)
    researcher_id_to_fname = {r["id"]: researcher_fname(r) for r in researchers}

    check_unique("papers",      paper_id_to_fname)
    check_unique("researchers", researcher_id_to_fname)

    for base, name, pid in sorted(renamed, key=lambda x: x[1]):
        print(f"    disambiguated: {base!r} → {name!r}  ({pid})")

    # topic/subtopic id → fname
    topic_id_to_fname  = {}
    subtopic_to_parent = {}

    for t in topics_raw:
        tf = topic_fname(t)
        topic_id_to_fname[t["id"]] = tf
        for s in t.get("subtopics", []):
            sf = subtopic_fname(s)
            topic_id_to_fname[s["id"]] = sf
            subtopic_to_parent[s["id"]] = tf

    # Topics and subtopics share the Topics/ folder, so they must be unique together.
    check_unique("topics+subtopics", topic_id_to_fname)

    # reverse: topic_id → [paper_fname]
    topic_to_papers = {tid: [] for tid in topic_id_to_fname}
    for p in papers:
        pf = paper_id_to_fname[p["id"]]
        for tid in p.get("topics", []):
            if tid in topic_to_papers:
                topic_to_papers[tid].append(pf)

    # reverse: topic_id → [researcher_fname]
    topic_to_researchers = {tid: [] for tid in topic_id_to_fname}
    for r in researchers:
        rf = researcher_id_to_fname[r["id"]]
        for tid in r.get("topics", []):
            if tid in topic_to_researchers:
                topic_to_researchers[tid].append(rf)

    # paper_id → [researcher_fname]  (authors)
    paper_to_researchers = {p["id"]: [] for p in papers}
    for r in researchers:
        rf = researcher_id_to_fname[r["id"]]
        for pid in r.get("key_papers", []):
            if pid in paper_to_researchers:
                paper_to_researchers[pid].append(rf)

    created = []

    # ── papers ──────────────────────────────────────────────────────────────
    for p in papers:
        pf   = paper_id_to_fname[p["id"]]
        tag  = p.get("tag", "")
        url  = p.get("url", "")
        auth = p.get("authors", [])
        year = p.get("year", "")
        jour = p.get("journal", "")
        sec  = p.get("section", "")
        summ = (p.get("summary") or "").strip()

        topics_links = [wikilink(topic_id_to_fname[tid])
                        for tid in p.get("topics", [])
                        if tid in topic_id_to_fname]
        res_links    = [wikilink(rf) for rf in paper_to_researchers[p["id"]]]

        fm_authors = "\n".join(f"  - {a}" for a in auth)
        fm_topics  = "\n".join(f'  - "[[{topic_id_to_fname[tid]}]]"'
                               for tid in p.get("topics", [])
                               if tid in topic_id_to_fname)

        ytags = [PROJECT_NAME.lower().replace(" ", "-"), "paper"]
        if tag:
            ytags.append(tag.replace("🇰🇷","kr").replace("🌐","intl").replace("📐","method"))

        md = f"""---
type: paper
id: {p["id"]}
title: "{p['title'].replace('"', "'")}"
authors:
{fm_authors}
year: {year}
journal: "{jour}"
section: "{sec}"
tag: "{tag}"
url: "{url}"
project: "{PROJECT_NAME}"
topics:
{fm_topics}
tags: [{", ".join(ytags)}]
---

# {p['title']}

**{" · ".join(filter(None, [", ".join(auth), str(year), jour]))}**{"  " + tag if tag else ""}
{"[↗ Full paper](" + url + ")" if url else ""}
{"**Section:** " + sec if sec else ""}

## Abstract

{summ if summ else "_No abstract available._"}

## Related Topics
{chr(10).join("- " + l for l in topics_links) if topics_links else "_None_"}

## Researchers / Authors
{chr(10).join("- " + l for l in res_links) if res_links else "_None listed_"}
"""
        created.append(write(os.path.join(pap_dir, pf + ".md"), md.strip() + "\n"))

    # ── topics & subtopics ───────────────────────────────────────────────────
    for t in topics_raw:
        tf    = topic_fname(t)
        label = t.get("label_en") or t.get("label", t["id"])
        desc  = (t.get("description") or "").strip()
        hsec  = t.get("handbook_section") or t.get("label_en", "")
        color = t.get("color", "")

        subs      = t.get("subtopics", [])
        sub_links = [wikilink(subtopic_fname(s)) for s in subs]

        res_links = sorted(set(wikilink(rf) for rf in topic_to_researchers.get(t["id"], [])))

        all_paper_links = set(wikilink(pf) for pf in topic_to_papers.get(t["id"], []))
        for s in subs:
            for pf in topic_to_papers.get(s["id"], []):
                all_paper_links.add(wikilink(pf))
        all_paper_links = sorted(all_paper_links)

        md = f"""---
type: topic
id: {t["id"]}
label: "{label}"
color: "{color}"
handbook_section: "{hsec}"
project: "{PROJECT_NAME}"
tags: [{PROJECT_NAME.lower().replace(" ","-")}, topic]
---

# {label}

{desc if desc else ""}
{"**Handbook section:** " + hsec if hsec else ""}

## Subtopics
{chr(10).join("- " + l for l in sub_links) if sub_links else "_None_"}

## Papers
{chr(10).join("- " + l for l in all_paper_links) if all_paper_links else "_None_"}

## Researchers
{chr(10).join("- " + l for l in res_links) if res_links else "_None_"}
"""
        created.append(write(os.path.join(top_dir, tf + ".md"), md.strip() + "\n"))

        for s in subs:
            sf       = subtopic_fname(s)
            slabel   = s.get("label_en") or s.get("label", s["id"])
            concepts = [str(c) for c in s.get("key_concepts", [])]
            sp_links = sorted(set(wikilink(pf) for pf in topic_to_papers.get(s["id"], [])))
            sr_links = sorted(set(wikilink(rf) for rf in topic_to_researchers.get(s["id"], [])))

            md_s = f"""---
type: subtopic
id: {s["id"]}
label: "{slabel}"
parent_topic: "[[{tf}]]"
project: "{PROJECT_NAME}"
tags: [{PROJECT_NAME.lower().replace(" ","-")}, subtopic]
---

# {slabel}

**Parent topic:** [[{tf}]]

## Key Concepts
{chr(10).join("- " + c for c in concepts) if concepts else "_None_"}

## Papers
{chr(10).join("- " + l for l in sp_links) if sp_links else "_None_"}

## Researchers
{chr(10).join("- " + l for l in sr_links) if sr_links else "_None_"}
"""
            created.append(write(os.path.join(top_dir, sf + ".md"), md_s.strip() + "\n"))

    # ── researchers ──────────────────────────────────────────────────────────
    for r in researchers:
        rf    = researcher_id_to_fname[r["id"]]
        tag   = r.get("tag", "")
        affil = r.get("affiliation", "")
        web   = r.get("website", "")

        topic_links = [wikilink(topic_id_to_fname[tid])
                       for tid in r.get("topics", [])
                       if tid in topic_id_to_fname]
        paper_links = [wikilink(paper_id_to_fname[pid])
                       for pid in r.get("key_papers", [])
                       if pid in paper_id_to_fname]

        ytags = [PROJECT_NAME.lower().replace(" ", "-"), "researcher"]
        if tag:
            for ch in ["🇰🇷","🌐","📐"]:
                if ch in tag:
                    ytags.append({"🇰🇷":"kr","🌐":"intl","📐":"method"}[ch])

        md = f"""---
type: researcher
id: {r["id"]}
name: "{r['name']}"
affiliation: "{affil}"
tag: "{tag}"
website: "{web}"
project: "{PROJECT_NAME}"
tags: [{", ".join(ytags)}]
---

# {r['name']}

**Affiliation:** {affil}{"  " + tag if tag else ""}
{"[↗ Website](" + web + ")" if web else ""}

## Research Topics
{chr(10).join("- " + l for l in topic_links) if topic_links else "_None_"}

## Key Papers
{chr(10).join("- " + l for l in paper_links) if paper_links else "_None_"}
"""
        created.append(write(os.path.join(res_dir, rf + ".md"), md.strip() + "\n"))

    # ── index note ───────────────────────────────────────────────────────────
    topic_index = "\n".join(f"- {wikilink(topic_fname(t))} — {(t.get('label_en') or t.get('label',''))}"
                            for t in topics_raw)
    paper_index = "\n".join(f"- {wikilink(paper_id_to_fname[p['id']])} ({p.get('journal','')} {p.get('year','')})"
                            for p in papers)
    res_index   = "\n".join(f"- {wikilink(researcher_id_to_fname[r['id']])} — {r.get('affiliation','')}"
                            for r in researchers)

    index_md = f"""---
type: index
project: "{PROJECT_NAME}"
tags: [{PROJECT_NAME.lower().replace(" ","-")}, index]
---

# {PROJECT_NAME}

> Ontology-based research map. Click any node to explore connections.
> Live D3 visualization: see the repo README for the GitHub Pages link.

## Topics ({len(topics_raw)})
{topic_index}

## Papers ({len(papers)})
{paper_index}

## Researchers ({len(researchers)})
{res_index}
"""
    write(os.path.join(VAULT, PROJECT_NAME + ".md"), index_md.strip() + "\n")

    # ── vault CLAUDE.md ──────────────────────────────────────────────────────
    claude_md = f"""\
# Claude context for this vault

## What's in here
{VAULT_BLURB}
Notes are connected by Obsidian wikilinks: Papers / Topics / Researchers.

## Note conventions
- Frontmatter `type:` = paper | topic | subtopic | researcher | index
- Wikilinks: `[[Author et al. YYYY]]` for papers, `[[Topic Label]]` for topics,
  `[[Full Name]]` for researchers
- Papers sharing a first author and year get an APA suffix: `2018a`, `2018b`

## Do not edit notes here
Every note is generated. Edit the source YAML instead:

```
data/ontology/{{topics,papers,researchers}}.yaml
python scripts/build_vault.py     # regenerate this vault
python scripts/build_graph.py     # regenerate the web graph
```

Stale notes are pruned automatically; hand-written notes without generator
frontmatter are left alone.
"""
    write(os.path.join(VAULT, "CLAUDE.md"), claude_md)

    # ── prune notes left over from a previous run ────────────────────────────
    for fname in prune_stale([pap_dir, top_dir, res_dir], created):
        print(f"    pruned stale note: {fname}")

    print(f"Built vault: {len(created)} notes + index + CLAUDE.md")
    print(f"  → {VAULT}")


if __name__ == "__main__":
    build()
