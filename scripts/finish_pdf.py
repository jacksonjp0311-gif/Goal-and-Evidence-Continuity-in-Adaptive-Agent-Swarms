"""Set PDF metadata and write one gallery image per page."""

from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = ROOT / "paper" / "whitepaper.pdf"
PAGE_DIR = ROOT / "docs" / "pages"

METADATA = {
    "title": "Goal and Evidence Continuity in Adaptive Agent Swarms",
    "author": "James Paul Jackson",
    "subject": "Runtime contracts and an evaluation protocol for Pegasus",
    "keywords": "adaptive agents, durable execution, goal contracts, evidence applicability, Pegasus",
    "creator": "James Paul Jackson",
    "producer": "Version 1.1, 8 November 2026",
}


def main():
    document = pymupdf.open(PDF_PATH)
    document.set_metadata(METADATA)
    document.saveIncr()
    PAGE_DIR.mkdir(parents=True, exist_ok=True)
    for old in PAGE_DIR.glob("page-*.png"):
        old.unlink()
    lines = [
        "# Page gallery",
        "",
        "Each image is one page of [whitepaper.pdf](../../paper/whitepaper.pdf), in order.",
        "",
        "| Page | Image |",
        "| --- | --- |",
    ]
    matrix = pymupdf.Matrix(1.7, 1.7)
    for index, page in enumerate(document, start=1):
        name = f"page-{index:03d}.png"
        pixmap = page.get_pixmap(matrix=matrix, alpha=False)
        pixmap.save(PAGE_DIR / name)
        lines.append(f"| {index} | [page {index}]({name}) |")
    lines.append("")
    (PAGE_DIR / "index.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"pages {document.page_count}")


if __name__ == "__main__":
    main()
