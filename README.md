# Goal and Evidence Continuity in Adaptive Agent Swarms

**Runtime contracts and an evaluation protocol for Pegasus**

James Paul Jackson
Version 1.1 · 8 November 2026

This repository publishes the technical report. It specifies a runtime contract for accepted goal obligations and completion evidence in an adaptive agent swarm, and a protocol for evaluating that contract. Pegasus is the implementation setting. The report does not claim measured performance improvements.

## Read the paper

| Format | Link |
| --- | --- |
| PDF, view in the browser | [paper/whitepaper.pdf](https://github.com/jacksonjp0311-gif/Goal-and-Evidence-Continuity-in-Adaptive-Agent-Swarms/blob/main/paper/whitepaper.pdf) |
| PDF, download | [paper/whitepaper.pdf](https://github.com/jacksonjp0311-gif/Goal-and-Evidence-Continuity-in-Adaptive-Agent-Swarms/raw/refs/heads/main/paper/whitepaper.pdf) |
| Full Markdown | [paper/whitepaper.md](paper/whitepaper.md) |
| Page gallery | [docs/pages/index.md](docs/pages/index.md) |
| Word source | [source/whitepaper.docx](source/whitepaper.docx) |

The Markdown file is the full manuscript, with the same sections, equations, algorithms, tables, figures, and references as the PDF.

## Paper

- [Abstract](paper/whitepaper.md#sec-abstract)
- [1 Introduction](paper/whitepaper.md#sec-introduction)
- [2 Related work and research position](paper/whitepaper.md#sec-related)
- [2.1 Goals and verifiable delegation](paper/whitepaper.md#sec-goals)
- [2.2 Durable runtimes and evidence management](paper/whitepaper.md#sec-durable)
- [2.3 Scope of the proposed contribution](paper/whitepaper.md#sec-scope)
- [3 System model and assumptions](paper/whitepaper.md#sec-model)
- [3.1 Persistent goals and replaceable execution](paper/whitepaper.md#sec-persistent)
- [3.2 Evidence applicability](paper/whitepaper.md#sec-evidence)
- [3.3 Trust and failure assumptions](paper/whitepaper.md#sec-trust)
- [4 Runtime architecture](paper/whitepaper.md#sec-architecture)
- [5 Continuity protocol](paper/whitepaper.md#sec-protocol)
- [5.1 Graph mutation and delegation](paper/whitepaper.md#sec-graph)
- [5.2 Result acceptance and artifact changes](paper/whitepaper.md#sec-acceptance)
- [5.3 Failure recovery and external effects](paper/whitepaper.md#sec-failure)
- [5.4 Provider handoff and contract amendment](paper/whitepaper.md#sec-handoff)
- [6 Conditional correctness properties](paper/whitepaper.md#sec-properties)
- [6.1 Structural continuity](paper/whitepaper.md#sec-structural)
- [6.2 Semantic soundness under stronger assumptions](paper/whitepaper.md#sec-semantic)
- [6.3 Progress and impossibility boundaries](paper/whitepaper.md#sec-progress)
- [7 Admission based on verification demand](paper/whitepaper.md#sec-admission)
- [8 Implementation setting in Pegasus](paper/whitepaper.md#sec-pegasus)
- [9 Evaluation protocol](paper/whitepaper.md#sec-evaluation)
- [9.1 Questions and experimental layers](paper/whitepaper.md#sec-questions)
- [9.2 Fault scenarios and independent oracles](paper/whitepaper.md#sec-faults)
- [9.3 Baselines and ablations](paper/whitepaper.md#sec-baselines)
- [9.4 Metrics and statistical analysis](paper/whitepaper.md#sec-metrics)
- [10 Limitations and research risks](paper/whitepaper.md#sec-limitations)
- [11 Conclusion](paper/whitepaper.md#sec-conclusion)
- [Appendix A. Minimum reproducibility record](paper/whitepaper.md#sec-appendix)
- [References](paper/whitepaper.md#sec-references)

## Repository

| Path | Contents |
| --- | --- |
| `paper/whitepaper.md` | Full manuscript. |
| `paper/whitepaper.pdf` | Typeset PDF. |
| `source/whitepaper.docx` | Editable Word source generated from the manuscript. |
| `assets/figures/` | Figure 1 and Figure 2 as SVG and PNG. |
| `docs/pages/` | One PNG per PDF page, and the gallery index. |
| `scripts/build.ps1` | Rebuilds figures, Word, PDF, and the gallery. |
| `scripts/requirements.txt` | Python packages used by the build. |
| `REVIEW_NOTES.md` | Substantive corrections and unresolved limits. |
| `CHANGELOG.md` | Publication revisions. |
| `CITATION.cff` | Citation metadata. |

## Research status

The architecture, the two conditional propositions, and the evaluation protocol are proposed. They are not an implementation of the continuity kernel, and they are not experimental results. Snapshot acceptance is not mission closure, and a preserved obligation is not proof that the obligation captures the user's intent. What still has to be built and run is an executable transition system, reproducible counterexample tests, fair baselines under matched budgets, and measured completion and cost outcomes. Those limits are stated in the paper and in [REVIEW_NOTES.md](REVIEW_NOTES.md).

## Citation

Jackson, James Paul. 2026. *Goal and Evidence Continuity in Adaptive Agent Swarms: Runtime contracts and an evaluation protocol for Pegasus.* Version 1.1, 8 November 2026. https://github.com/jacksonjp0311-gif/Goal-and-Evidence-Continuity-in-Adaptive-Agent-Swarms

## Rebuild

From the repository root, with Python 3 and Microsoft Word installed:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build.ps1
```

The script installs the packages in `scripts/requirements.txt` for the current user, redraws the figures, renders `source/whitepaper.docx` from `paper/whitepaper.md`, exports the PDF through Word, writes `docs/pages/page-001.png` onward, and checks the manuscript counts. Word is the PDF exporter. The Python packages are `python-docx`, `pymupdf`, and `pillow`.

This repository does not add a license file.
