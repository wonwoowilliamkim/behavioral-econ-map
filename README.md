# Behavioral Public Economics — Interactive Research Map

> An Obsidian-style, browser-based knowledge graph of the **behavioral public economics** literature — built from papers cited in Bernheim & Taubinsky (2018), the authoritative handbook chapter on the field.

**Live demo:** [GitHub Pages](https://wonwoowilliamkim.github.io/behavioral-econ-map/) _(deploy instructions below)_

---

## What Is This?

This project turns an academic literature into an **interactive, explorable network**. Every paper, researcher, and topic in the graph is a clickable node. Click a paper → see its summary, journal, handbook section, and every connected author and topic. Click a researcher → see all their papers at once. Filter by node type. Search across the entire corpus with `⌘K`.

The ontology is grounded in **Bernheim & Taubinsky (2018) "Behavioral Public Economics"** (NBER WP 24828, _Handbook of Behavioral Economics_ Vol. 1) — the most comprehensive survey of the field to date. Only papers directly cited in that handbook chapter are included.

---

## Field Coverage

The map covers **six thematic clusters** mirroring the handbook's structure:

| Handbook Section | Topic Cluster | Key Papers |
|---|---|---|
| §2 | **Behavioral Welfare Economics** | Bernheim-Rangel (2009), Chetty (2015) |
| §3.2 | **Corrective Taxation** | Allcott-Taubinsky (2015), Gruber-Kőszegi (2001) |
| §3.3 | **Distributional Concerns** | Allcott-Lockwood-Taubinsky (2018) |
| §3.4 | **Tax Salience** | Chetty-Looney-Kroft (2009), Finkelstein (2009) |
| §3.5 | **Nudges & Defaults** | Thaler-Sunstein (2003), Madrian-Shea (2001) |
| §4–5 | **Saving & Earnings** | Laibson (1997), Bhargava-Manoli (2015) |

**26 papers · 28 researchers · 7 topic clusters · 22 subtopics · 236+ connections**

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
│       ├── topics.yaml        # 7 topic clusters, 22 subtopics with handbook sections
│       ├── papers.yaml        # 26 papers from Bernheim-Taubinsky (2018) w24828
│       └── researchers.yaml   # 28 researchers, key papers, affiliations
│
├── scripts/
│   └── build_graph.py         # YAML → site/graph.json (D3 input)
│
├── site/                      # Static site — deploy to GitHub Pages
│   ├── index.html             # Layout, header, filter bar, detail panel
│   ├── style.css              # Dark-mode design system
│   ├── graph.js               # D3 v7 force-directed graph, tooltips, highlight
│   ├── search.js              # Client-side fuzzy search with keyboard nav
│   └── graph.json             # Auto-generated — do not edit directly
│
└── w24828.pdf                 # Source: Bernheim & Taubinsky (2018) NBER WP
```

---

## How to Run Locally

### 1. Prerequisites

```bash
pip install pyyaml
```

### 2. Build the graph

```bash
python scripts/build_graph.py
# → Built graph: 84 nodes, 236 links → site/graph.json
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

```bash
# From repo root
git checkout -b gh-pages   # or use your existing main branch
git add site/
git commit -m "deploy site"
git push origin gh-pages

# In GitHub repo → Settings → Pages → Source: gh-pages branch / /site folder
```

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

Journals covered: _AER, QJE, JPE, REStud, Econometrica, JPubE, JEEA, REStat, AEA P&P_.

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

3. If needed, add the researcher to `researchers.yaml`
4. Rebuild: `python scripts/build_graph.py`

---

## Reference

- **Handbook chapter (source):** [Bernheim & Taubinsky (2018) NBER WP 24828](https://www.nber.org/papers/w24828)
- **Mini-course notes:** [Behavioral Public Economics Mini-Course](https://sites.google.com/view/behavioralpublic/home)
- **NBER working group:** NBER Behavioral Public Economics Working Group
