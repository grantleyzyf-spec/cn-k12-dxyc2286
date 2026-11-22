# China K-12 Subject Knowledge Graph

**19 subjects · 55 subject tracks · 12,269 knowledge nodes · 13,686 prerequisite edges (13,194 hard / 492 soft) · 80,539 diagnostic items · 4,375 curriculum-standard entries**, covering primary through senior high school in mainland China.

**[Browse the live site](https://grantleyzyf-spec.github.io/cn-k12-dxyc2286/)**

## What this is

A machine-readable knowledge graph of the Chinese K-12 curriculum. It is not a list of topics — every node carries the four things an adaptive system actually needs:

- **An observable mastery criterion** — what a student must be able to *do*, not "understand the chapter".
- **Node-level diagnostic items** — questions that test that specific node, not a whole unit.
- **A prerequisite structure** with two edge types: `hard` (you cannot proceed without it) and `soft` (helps, but is not blocking). 13,686 edges total (13,194 hard / 492 soft).
- **A curriculum-standard anchor** — 12,034 of 12,269 nodes are mapped to one of 4,375 standard entries, with the quoted excerpt and a confidence score.

Because the diagnostics are attached to nodes rather than units, the graph can be used directly for prerequisite diagnosis: a wrong answer walks the hard edges upward and returns a minimal, ordered list of missing nodes.

## Coverage

19 subjects across 55 subject tracks (13 mathematics tracks, 10 physics, 9 chemistry, 8 geography, plus single-track subjects), covering primary, junior-high and senior-high stages. Chinese mathematics, English, physics, chemistry, biology, politics, history, geography, information technology, and others.

## Layout

```
data/topics.json                  knowledge nodes (id, subject, stage, grade, mastery criterion)
data/dependencies.json            prerequisite edges (hard / soft)
data/cn-curriculum-standards.json curriculum-standard entries + node mapping + confidence
data/<subject>-<edition>/         per-subject learning, exam and lecture shards
scripts/, _build_*.py             generators, audits and quality gates
topics/, learn/, diagnose/        static site (GitHub Pages)
```

## Using it

- Static JSON, no server, no login. Fetch `data/topics.json` and `data/dependencies.json` and build your own graph.
- The site is a reference implementation: explore, diagnose, and learning-record pages all read the same JSON.
- Suggested entry points: `explore/` for the graph view, `diagnose/` for the prerequisite-diagnosis demo.

## Data quality

Every node is checked by automated gates before merge: prerequisite edges must not create cycles, diagnostic answers must match the mastery criterion, and curriculum mappings must resolve to an existing standard entry. Issues from teachers and students are tracked with the issue templates in this repository.

## License

Split licensing, because the two halves have different constraints:

- **Code** (site generator, build/audit scripts, HTML/CSS/JS, tests) — **MIT**, see `LICENSE`.
- **Data** (`data/` — nodes, edges, items, curriculum-standard excerpts) — **CC BY-NC 4.0**, see `LICENSE-DATA`. Non-commercial because the graph quotes excerpts from Chinese curriculum standards and textbook editions.

For commercial licensing of the dataset, open an issue or use the contact page on the site.

## Citation

If you use the graph in research or teaching, cite it via `CITATION.cff`:

> grantleyzyf-spec (2026). *China K-12 Subject Knowledge Graph (cn-k12-dxyc2286)*, v1.0.0. https://github.com/grantleyzyf-spec/cn-k12-dxyc2286

## Contributing

Corrections from teachers are the most valuable input. See `CONTRIBUTING.md` — data corrections go through the issue templates, code changes through pull requests.
