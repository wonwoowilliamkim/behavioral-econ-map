# Behavioral Public Economics — Interactive Research Map

> An Obsidian-style, browser-based knowledge graph of the **behavioral public economics** literature — anchored on Bernheim & Taubinsky (2018), the authoritative handbook chapter on the field, and extended with the NBER Behavioral Public Economics Boot Camp reading list.

**Live demo:** [GitHub Pages](https://wonwoowilliamkim.github.io/behavioral-econ-map/) _(deploy instructions below)_

---

## What Is This?

This project turns an academic literature into an **interactive, explorable network**. Every paper, researcher, and topic in the graph is a clickable node. Click a paper → see its summary, journal, handbook section, and every connected author and topic. Click a researcher → see all their papers at once. Filter by node type. Search across the entire corpus with `⌘K`.

The ontology is grounded in **Bernheim & Taubinsky (2018) "Behavioral Public Economics"** (NBER WP 24828, _Handbook of Behavioral Economics_ Vol. 1) — the most comprehensive survey of the field to date. The handbook chapter supplies the backbone: seven topic clusters keyed to its section numbers. Four further clusters — insurance, household finance, behavioral IO, and inequality — come from the **NBER Behavioral Public Economics Boot Camp** reading list, and are marked as `module` rather than `§` in their `handbook_section` field.

---

## Field Coverage

The map covers **eleven topic clusters** — seven keyed to the handbook's section numbers, four drawn from the boot camp modules:

| Source | Topic Cluster | Subtopics | Papers | Example |
|---|---|---|---|---|
| §2 | **Behavioral Welfare Economics** | 3 | 17 | Bernheim-Rangel (2009 QJE) |
| §3 | **Corrective Taxation & Policy** | 4 | 21 | Gruber-Kőszegi (2001 QJE) |
| §3.5 | **Nudges & Default Effects** | 3 | 15 | Madrian-Shea (2001 QJE) |
| §4–§5 | **Sludge & Administrative Burden** | 2 | 3 | Bhargava-Manoli (2015 AER) |
| §4 | **Present Bias & Self-Control** | 3 | 16 | Laibson (1997 QJE) |
| §5 | **Earnings & Labor Policy** | 2 | 11 | Chetty (2008 JPE) |
| cross-cutting | **Empirical Methods** | 3 | 31 | Chetty-Looney-Kroft (2009 AER) |
| Boot camp module | **Behavioral & Social Insurance** | 4 | 22 | Abaluck-Gruber (2011 AER) |
| Boot camp module | **Household Finance & Consumer Credit** | 3 | 6 | Gathergood-Mahoney (2019 AER) |
| Boot camp module | **Behavioral Industrial Organization** | 2 | 2 | Grubb (2015 JEP) |
| Boot camp module | **Inequality, Mobility & Opportunity** | 2 | 3 | Stantcheva (2021 QJE) |

**73 papers · 74 researchers · 11 topic clusters · 31 subtopics · 189 nodes · 547 connections**

> Paper counts per cluster include papers attached via that cluster's subtopics, and a paper can belong to several clusters — so the column sums to more than 73. The live site's stats bar is generated from `graph.json` and is always authoritative.

---

## Key Ideas Mapped

### Behavioral Welfare Economics (§2)
The central challenge: when choices may not reveal true preferences, how do we evaluate welfare? Bernheim & Rangel (2009) propose the _unambiguous choice relation_ P\* — a minimal welfare criterion that avoids interpersonal comparisons while still saying something substantive. Chetty (2015) argues for a more pragmatic _sufficient statistics_ approach: use reduced-form behavioral wedges without specifying a full cognitive model.

### Corrective Taxation (§3)
The classic Pigouvian tax (= externality) gets extended to _internalities_ — harms consumers impose on their future selves through biased choices. The optimal corrective tax becomes:

```
τ* = marginal externality + average internality
```

Allcott & Taubinsky (2015) operationalize this using a debiasing experiment in the lightbulb market. Gruber & Kőszegi (2001) apply it to cigarette taxation under quasi-hyperbolic discounting.

### Tax Salience (§3.4)
Chetty, Looney & Kroft (2009) show that when taxes are not included in posted prices, consumers underreact by a factor σ ≈ 0.06–0.35. This has implications for both behavioral welfare analysis and the political economy of taxation (Finkelstein 2009).

### Nudges & Defaults (§3.5)
Libertarian paternalism (Thaler & Sunstein 2003): since defaults inevitably influence behavior, policy-makers should choose defaults that maximize welfare. Madrian & Shea (2001) document that auto-enrollment raises 401(k) participation from ~49% to ~86%.

---

## Project Structure

```
behavioral-econ-map/
│
├── data/
│   └── ontology/
│       ├── topics.yaml        # 11 topic clusters, 31 subtopics with handbook sections
│       ├── papers.yaml        # 73 papers — w24828 bibliography + boot camp reading list
│       └── researchers.yaml   # 74 researchers, key papers, affiliations
│
├── scripts/
│   ├── build_graph.py         # YAML → site/graph.json (the web graph)
│   └── build_vault.py         # YAML → vault/ (Obsidian notes)
│
├── site/                      # ← the only folder published to the web
│   ├── index.html             # Layout, header, filter bar, detail panel
│   ├── style.css              # Dark-mode design system
│   ├── graph.js               # D3 v7 force-directed graph, tooltips, highlight
│   ├── search.js              # Client-side scored search with keyboard nav
│   └── graph.json             # Auto-generated — do not edit directly
│
├── vault/                     # Obsidian vault — open THIS folder, not the repo
│   ├── .obsidian/             # Graph colors, plugins (tracked; workspace.json is not)
│   ├── Papers/ Topics/ Researchers/
│   └── Behavioral Public Economics.md
│
├── .github/workflows/
│   └── deploy.yml             # Push to main → rebuild graph.json → publish site/
│
└── w24828.pdf                 # Source: Bernheim & Taubinsky (2018) NBER WP
```

The ontology, the scripts, the vault and the source PDF stay in the repository
but are not uploaded to the web host — the workflow publishes `site/` only.

---

## How to Run Locally

### 1. Prerequisites

```bash
pip install pyyaml
```

### 2. Build the graph

```bash
python scripts/build_graph.py
# → Built graph: 189 nodes, 547 links
#   → site/graph.json
```

### 3. Serve the site

```bash
# Python 3
python -m http.server 8080 --directory site
# then open http://localhost:8080
```

> **Why a local server?** The site loads `graph.json` via `fetch()`, which requires a server due to browser CORS policy. Opening `index.html` directly from the filesystem won't work.

---

## GitHub Pages Deployment

Deployment is automated by [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml).
Any push to `main` re-runs `build_graph.py` in CI and republishes — so committing
edited YAML is enough; a stale `graph.json` in the commit gets overwritten.

```bash
git add data/ontology/ site/graph.json
git commit -m "Add papers to ontology"
git push origin main          # → Actions rebuilds and deploys
```

One-time setup: **Settings → Pages → Source: GitHub Actions** (not "Deploy from a
branch"). There is no `gh-pages` branch and no `docs/` folder — the workflow
uploads `site/` as the artifact.

---

## UI Features

| Feature | How |
|---|---|
| **Explore** | Click any node to highlight its neighborhood and open the detail panel |
| **Search** | `⌘K` (Mac) / `Ctrl+K` (Win) to focus search; arrow keys to navigate results |
| **Filter** | Header buttons filter by node type: Topics / Subtopics / Papers / Researchers |
| **Zoom & Pan** | Scroll to zoom · Drag to pan · `+` / `−` / `⌂` buttons |
| **Drag nodes** | Nodes can be repositioned by dragging |
| **Tooltips** | Hover any node for a quick-glance summary |
| **Paper panel** | Click a paper → see journal, year, handbook section, abstract, links |

---

## Data Sources

All papers are from the bibliography of:

> Bernheim, B. D., & Taubinsky, D. (2018). **Behavioral Public Economics**. In B. D. Bernheim, S. DellaVigna, & D. Laibson (Eds.), _Handbook of Behavioral Economics: Applications and Foundations_, Vol. 1 (pp. 381–516). Elsevier. [NBER WP 24828](https://www.nber.org/papers/w24828)

Papers added from the boot camp reading list extend beyond that bibliography.
Outlets covered are led by _AER_ and _QJE_ (roughly half the corpus between them),
followed by _Econometrica, JPE, JPubE, REStud, AEJ: Applied, AEJ: Economic Policy,
JEEA_, plus review outlets (_JEL, JEP, Annual Review of Economics_), NBER working
papers, and _Handbook of Behavioral Economics_ chapters.

---

## Obsidian Vault

The same ontology is also rendered as a linked-note vault. In Obsidian, open
`vault/` — **not** the repository root, or Obsidian will index the YAML and
JavaScript too and the graph view becomes unusable.

```bash
pip install pyyaml
python scripts/build_vault.py
# → Built vault: 189 notes + index + CLAUDE.md
```

| | |
|---|---|
| **Note types** | `paper` · `topic` · `subtopic` · `researcher` · `index` (frontmatter `type:`) |
| **Wikilinks** | `[[Author et al. YYYY]]` · `[[Topic Label]]` · `[[Full Name]]` |
| **Same-name papers** | APA suffix on the year — `Allcott et al. 2018a` / `2018b` |
| **Editing** | Don't. Notes are generated; edit `data/ontology/*.yaml` and rerun |

Renamed and removed notes are pruned on each run, so the vault never
accumulates orphans. A note without generator frontmatter is left untouched,
so you can keep hand-written notes alongside the generated ones.

---

## How to Add Papers

1. Open `data/ontology/papers.yaml`
2. Add an entry following the existing format:

```yaml
- id: your_unique_id
  title: "Full paper title"
  authors: [LastName1, LastName2]
  year: 2024
  journal: AER
  section: "§3.2 Corrective Taxation"       # optional
  topics: [internality_tax, corrective_policy]  # must match subtopic/topic IDs
  url: https://doi.org/...
  summary: >
    2-3 sentence summary of the paper's contribution.
```

3. If needed, add the researcher to `researchers.yaml` — an `authored` edge is
   drawn from the researcher's `key_papers` list, not from the paper's
   `authors`, so a paper without a matching entry there stays unlinked
4. Rebuild both renderings:
   ```bash
   python scripts/build_graph.py    # web
   python scripts/build_vault.py    # Obsidian
   ```
5. Commit and push — Actions redeploys the site automatically

---

## Reference

- **Handbook chapter (source):** [Bernheim & Taubinsky (2018) NBER WP 24828](https://www.nber.org/papers/w24828)
- **Mini-course notes:** [Behavioral Public Economics Mini-Course](https://sites.google.com/view/behavioralpublic/home)
- **NBER working group:** NBER Behavioral Public Economics Working Group
