"""Check that the publication still matches the reviewed manuscript."""

import re
import sys
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
MD = (ROOT / "paper" / "whitepaper.md").read_text(encoding="utf-8")
PDF = pymupdf.open(ROOT / "paper" / "whitepaper.pdf")
TEXT = "\n".join(page.get_text() for page in PDF)
PAGES = sorted((ROOT / "docs" / "pages").glob("page-*.png"))

errors = []


def need(condition, message):
    if not condition:
        errors.append(message)


for number in range(1, 10):
    need(f"\\tag{{{number}}}" in MD, f"missing equation tag {number}")
need(MD.count("**Algorithm ") == 2, "expected two algorithms")
need(MD.count("*Table ") == 3, "expected three tables")
need(MD.count("*Figure ") == 2, "expected two figures")
need(all(f"[{n}] " in MD[MD.find("## References"):] for n in range(1, 15)), "expected references 1-14")
need("James Paul Jackson" in TEXT, "PDF is missing the author")
need("Version 1.1" in TEXT, "PDF is missing the version")
need("Proposition 1" in TEXT and "Proposition 2" in TEXT, "PDF is missing a proposition")
need("Algorithm 1" in TEXT and "Algorithm 2" in TEXT, "PDF is missing an algorithm")
for symbol in ("⇒", "∀", "⊨", "⊎", "≤", "∑"):
    need(symbol in TEXT, f"PDF text is missing {symbol}")
need(len(PAGES) == PDF.page_count, f"gallery has {len(PAGES)} images for {PDF.page_count} pages")
names = [path.name for path in PAGES]
need(names == [f"page-{i:03d}.png" for i in range(1, PDF.page_count + 1)], "gallery names are not sequential")

prose = [
    ROOT / "README.md",
    ROOT / "REVIEW_NOTES.md",
    ROOT / "CHANGELOG.md",
    ROOT / "CITATION.cff",
    ROOT / "paper" / "whitepaper.md",
    ROOT / "docs" / "pages" / "index.md",
]
blob = "\n".join(path.read_text(encoding="utf-8") for path in prose if path.exists())
for token in ("C:\\Users", "/home/", "localhost", "127.0.0.1", "TODO", "PLACEHOLDER", "lorem ipsum", "TKTK"):
    if token.lower() in blob.lower():
        errors.append(f"publication contains {token}")

need((ROOT / "source" / "whitepaper.docx").exists(), "missing docx")
need((ROOT / "assets" / "figures" / "figure-1.svg").exists(), "missing figure 1 svg")
need((ROOT / "assets" / "figures" / "figure-2.svg").exists(), "missing figure 2 svg")
meta = PDF.metadata or {}
need("Jackson" in (meta.get("author") or ""), f"PDF author metadata is {meta.get('author')!r}")
need("Goal and Evidence Continuity" in (meta.get("title") or ""), "PDF title metadata is incomplete")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"ok pages={PDF.page_count} chars={len(TEXT)}")
