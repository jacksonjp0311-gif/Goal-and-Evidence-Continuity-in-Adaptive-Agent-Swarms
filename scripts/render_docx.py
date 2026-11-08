"""Render paper/whitepaper.md to source/whitepaper.docx.

The Markdown file is authoritative. This script understands the subset used
by the manuscript: headings, paragraphs, lists, tables, fenced code, images,
display math, and inline math.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Emu, Inches, Pt, RGBColor, Twips
from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "paper" / "whitepaper.md"
DOCX_PATH = ROOT / "source" / "whitepaper.docx"
CONTENT_WIDTH = Inches(6.5)

M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
XML_NS = "http://www.w3.org/XML/1998/namespace"
INK = RGBColor(0x1C, 0x1C, 0x1C)
NAVY = RGBColor(0x12, 0x32, 0x4D)
LINK = RGBColor(0x1A, 0x36, 0x5D)

SYMBOLS = {
    "Gamma": "Γ",
    "sigma": "σ",
    "tau": "τ",
    "Omega": "Ω",
    "Pi": "Π",
    "varphi": "φ",
    "phi": "φ",
    "forall": "∀",
    "in": "∈",
    "Rightarrow": "⇒",
    "land": "∧",
    "wedge": "∧",
    "models": "⊨",
    "sum": "∑",
    "leq": "≤",
    "le": "≤",
    "uplus": "⊎",
    "ldots": "…",
    "cdot": "·",
}


def M(tag):
    return etree.Element(f"{{{M_NS}}}{tag}")


def set_run_font(run, name, size, bold=False, italic=False, color=None, super_=False, sub_=False):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.superscript = super_
    run.font.subscript = sub_
    if color is not None:
        run.font.color.rgb = color
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs"):
        rFonts.set(qn(attr), name)


def shade_cell(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)


def set_cell_borders(cell, color="BFBFBF", sz="4"):
    tcPr = cell._tc.get_or_add_tcPr()
    borders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), sz)
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), color)
        borders.append(el)
    tcPr.append(borders)


def set_cell_width(cell, width):
    tcPr = cell._tc.get_or_add_tcPr()
    tcW = tcPr.find(qn("w:tcW"))
    if tcW is None:
        tcW = OxmlElement("w:tcW")
        tcPr.append(tcW)
    dxa = str(int(width.twips)) if hasattr(width, "twips") else str(int(width))
    tcW.set(qn("w:w"), dxa)
    tcW.set(qn("w:type"), "dxa")


def set_table_widths(table, widths):
    table.autofit = False
    table.allow_autofit = False
    tbl = table._tbl
    tblPr = tbl.tblPr
    tblW = tblPr.find(qn("w:tblW"))
    if tblW is None:
        tblW = OxmlElement("w:tblW")
        tblPr.append(tblW)
    total = sum(int(w.twips) for w in widths)
    tblW.set(qn("w:w"), str(total))
    tblW.set(qn("w:type"), "dxa")
    grid = tbl.find(qn("w:tblGrid"))
    if grid is not None:
        for child in list(grid):
            grid.remove(child)
    else:
        grid = OxmlElement("w:tblGrid")
        tblPr.addnext(grid)
    for width in widths:
        gc = OxmlElement("w:gridCol")
        gc.set(qn("w:w"), str(int(width.twips)))
        grid.append(gc)
    for row in table.rows:
        for cell, width in zip(row.cells, widths):
            set_cell_width(cell, width)


def prevent_row_split(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(OxmlElement("w:cantSplit"))


def mark_header_row(row):
    trPr = row._tr.get_or_add_trPr()
    header = OxmlElement("w:tblHeader")
    header.set(qn("w:val"), "true")
    trPr.append(header)


def no_table_borders(table):
    tblPr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "nil")
        borders.append(el)
    tblPr.append(borders)


def add_bottom_border(paragraph, color="1C1C1C", sz="8"):
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), sz)
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), color)
    pBdr.append(bottom)
    pPr.append(pBdr)


def add_page_field(paragraph):
    run = paragraph.add_run()
    set_run_font(run, "Cambria", 9, color=INK)
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    r = run._r
    r.append(begin)
    r.append(instr)
    r.append(separate)
    shown = OxmlElement("w:t")
    shown.text = "1"
    r.append(shown)
    r.append(end)


BOOKMARK_ID = 1


def add_bookmark(paragraph, name):
    global BOOKMARK_ID
    start = OxmlElement("w:bookmarkStart")
    start.set(qn("w:id"), str(BOOKMARK_ID))
    start.set(qn("w:name"), name)
    end = OxmlElement("w:bookmarkEnd")
    end.set(qn("w:id"), str(BOOKMARK_ID))
    BOOKMARK_ID += 1
    paragraph._p.insert(0, start)
    paragraph._p.append(end)


def add_hyperlink(paragraph, text, url):
    if url.startswith("#"):
        hyperlink = OxmlElement("w:hyperlink")
        hyperlink.set(qn("w:anchor"), url[1:])
        run = OxmlElement("w:r")
        rPr = OxmlElement("w:rPr")
        rFonts = OxmlElement("w:rFonts")
        rFonts.set(qn("w:ascii"), "Cambria")
        rFonts.set(qn("w:hAnsi"), "Cambria")
        rFonts.set(qn("w:cs"), "Cambria")
        rPr.append(rFonts)
        color = OxmlElement("w:color")
        color.set(qn("w:val"), "1A365D")
        rPr.append(color)
        underline = OxmlElement("w:u")
        underline.set(qn("w:val"), "single")
        rPr.append(underline)
        run.append(rPr)
        t = OxmlElement("w:t")
        t.text = text
        run.append(t)
        hyperlink.append(run)
        paragraph._p.append(hyperlink)
        return
    part = paragraph.part
    rel_id = part.relate_to(
        url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True,
    )
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), rel_id)
    run = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    rFonts = OxmlElement("w:rFonts")
    rFonts.set(qn("w:ascii"), "Cambria")
    rFonts.set(qn("w:hAnsi"), "Cambria")
    rFonts.set(qn("w:cs"), "Cambria")
    rPr.append(rFonts)
    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), "22")
    rPr.append(sz)
    szCs = OxmlElement("w:szCs")
    szCs.set(qn("w:val"), "22")
    rPr.append(szCs)
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "1A365D")
    rPr.append(color)
    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "single")
    rPr.append(underline)
    run.append(rPr)
    t = OxmlElement("w:t")
    t.set(qn("xml:space"), "preserve")
    t.text = text
    run.append(t)
    hyperlink.append(run)
    paragraph._p.append(hyperlink)


class MathParser:
    def __init__(self, source):
        self.s = source.strip()
        self.i = 0
        self.n = len(self.s)

    def peek(self):
        return self.s[self.i] if self.i < self.n else ""

    def parse(self):
        nodes = self.parse_seq(None)
        if self.i < self.n:
            raise ValueError(f"Unparsed math at {self.s[self.i:]!r}")
        return nodes

    def parse_seq(self, stop):
        nodes = []
        while self.i < self.n and (stop is None or self.peek() not in stop):
            if self.peek() == " ":
                self.i += 1
                continue
            nodes.append(self.parse_atom())
        return nodes

    def parse_atom(self):
        node = self.parse_primary()
        sub = sup = None
        if self.peek() == "_":
            self.i += 1
            sub = self.parse_script()
        if self.peek() == "^":
            self.i += 1
            sup = self.parse_script()
        if sub is not None or sup is not None:
            return ("ss", node, sub, sup)
        return node

    def parse_script(self):
        self.skip_space()
        if self.peek() == "{":
            return ("seq", self.parse_group())
        return self.parse_primary()

    def parse_group(self):
        if self.peek() != "{":
            raise ValueError("expected {")
        self.i += 1
        nodes = self.parse_seq("}")
        if self.peek() != "}":
            raise ValueError("unclosed group")
        self.i += 1
        return nodes

    def skip_space(self):
        while self.peek() == " ":
            self.i += 1

    def parse_primary(self):
        self.skip_space()
        ch = self.peek()
        if ch == "\\":
            return self.parse_command()
        if ch == "{":
            return ("seq", self.parse_group())
        if ch == "":
            raise ValueError("unexpected end of math")
        self.i += 1
        return ("run", ch, False)

    def parse_command(self):
        self.i += 1
        if self.peek() in "{}":
            ch = self.peek()
            self.i += 1
            return ("run", ch, False)
        name = []
        while self.peek().isalpha():
            name.append(self.peek())
            self.i += 1
        if not name and self.peek():
            ch = self.peek()
            self.i += 1
            if ch in ",;:":
                return ("run", " ", False)
            return ("run", ch, False)
        command = "".join(name)
        if command in ("left", "right"):
            if self.peek() in "()[]{}|.":
                self.i += 1
            return ("run", "", False)
        if command in ("quad",):
            return ("run", " ", False)
        if command in ("qquad",):
            return ("run", "  ", False)
        if command in SYMBOLS:
            return ("run", SYMBOLS[command], False)
        if command == "mathrm":
            group = self.parse_group()
            text = flatten_text(group)
            return ("run", text, True)
        if command == "hat":
            group = self.parse_group()
            return ("hat", ("seq", group))
        if command == "tag":
            self.parse_group()
            return ("run", "", False)
        raise ValueError(f"unsupported math command \\{command}")


def flatten_text(nodes):
    parts = []
    for node in nodes:
        kind = node[0]
        if kind == "run":
            parts.append(node[1])
        elif kind == "seq":
            parts.append(flatten_text(node[1]))
        elif kind == "ss":
            parts.append(flatten_text([node[1]]))
            if node[2] is not None:
                parts.append(flatten_text([node[2]]))
            if node[3] is not None:
                parts.append(flatten_text([node[3]]))
        elif kind == "hat":
            parts.append(flatten_text([node[1]]))
        else:
            raise ValueError(kind)
    return "".join(parts)


def math_run(text, plain):
    if text == "":
        return None
    r = M("r")
    if plain:
        rPr = M("rPr")
        sty = M("sty")
        sty.set(f"{{{M_NS}}}val", "p")
        rPr.append(sty)
        r.append(rPr)
    t = M("t")
    if text.startswith(" ") or text.endswith(" "):
        t.set(f"{{{XML_NS}}}space", "preserve")
    t.text = text
    r.append(t)
    return r


def emit_math(node):
    kind = node[0]
    if kind == "run":
        emitted = math_run(node[1], node[2])
        return emitted
    if kind == "seq":
        wrapper = M("e")
        fill_math(wrapper, node[1])
        return wrapper
    if kind == "hat":
        acc = M("acc")
        accPr = M("accPr")
        chr_el = M("chr")
        chr_el.set(f"{{{M_NS}}}val", "̂")
        accPr.append(chr_el)
        acc.append(accPr)
        e = M("e")
        fill_math(e, [node[1]])
        acc.append(e)
        return acc
    if kind == "ss":
        base, sub, sup = node[1], node[2], node[3]
        if sub is not None and sup is not None:
            el = M("sSubSup")
        elif sub is not None:
            el = M("sSub")
        else:
            el = M("sSup")
        e = M("e")
        fill_math(e, [base])
        el.append(e)
        if sub is not None:
            slot = M("sub")
            fill_math(slot, [sub])
            el.append(slot)
        if sup is not None:
            slot = M("sup")
            fill_math(slot, [sup])
            el.append(slot)
        return el
    raise ValueError(kind)


def fill_math(parent, nodes):
    for node in nodes:
        if node[0] == "seq":
            fill_math(parent, node[1])
            continue
        emitted = emit_math(node)
        if emitted is not None:
            parent.append(emitted)


def omml_from_latex(latex):
    nodes = MathParser(latex).parse()
    om = M("oMath")
    fill_math(om, nodes)
    return om


def extract_tag(latex):
    match = re.search(r"\\tag\{(\d+)\}", latex)
    number = match.group(1) if match else ""
    cleaned = re.sub(r"\\tag\{(\d+)\}", "", latex).strip()
    return cleaned, number


TOKEN = re.compile(
    r"(\*\*[^*]+?\*\*|\*[^*]+?\*|`[^`]+`|\[[^\]]+?\]\([^)]+?\)|\$[^$]+?\$)"
)


def add_inline(paragraph, text, size=11, color=INK, base_bold=False, base_italic=False):
    parts = TOKEN.split(text)
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            run = paragraph.add_run(part[2:-2])
            set_run_font(run, "Cambria", size, bold=True, italic=base_italic, color=color)
        elif part.startswith("*") and part.endswith("*"):
            run = paragraph.add_run(part[1:-1])
            set_run_font(run, "Cambria", size, bold=base_bold, italic=True, color=color)
        elif part.startswith("`") and part.endswith("`"):
            run = paragraph.add_run(part[1:-1])
            set_run_font(run, "Consolas", max(size - 1, 8), color=color)
        elif part.startswith("["):
            match = re.fullmatch(r"\[([^\]]+)\]\(([^)]+)\)", part)
            if match:
                add_hyperlink(paragraph, match.group(1), match.group(2))
            else:
                run = paragraph.add_run(part)
                set_run_font(run, "Cambria", size, color=color)
        elif part.startswith("$") and part.endswith("$"):
            om = omml_from_latex(part[1:-1])
            paragraph._p.append(om)
        else:
            run = paragraph.add_run(part)
            set_run_font(run, "Cambria", size, bold=base_bold, italic=base_italic, color=color)


def configure_styles(document):
    normal = document.styles["Normal"]
    normal.font.name = "Cambria"
    normal.font.size = Pt(11)
    normal.font.color.rgb = INK
    pf = normal.paragraph_format
    pf.space_after = Pt(8)
    pf.space_before = Pt(0)
    pf.line_spacing = 1.12
    rPr = normal.element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs"):
        rFonts.set(qn(attr), "Cambria")

    specs = {
        "Heading 1": (16, 16, 6, NAVY),
        "Heading 2": (13, 12, 4, NAVY),
    }
    for name, (size, before, after, color) in specs.items():
        style = document.styles[name]
        style.font.name = "Cambria"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = color
        style.font.italic = False
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.line_spacing = 1.05
        style.paragraph_format.keep_with_next = True
        rPr = style.element.get_or_add_rPr()
        rFonts = rPr.find(qn("w:rFonts"))
        if rFonts is None:
            rFonts = OxmlElement("w:rFonts")
            rPr.append(rFonts)
        for attr in ("w:ascii", "w:hAnsi", "w:cs"):
            rFonts.set(qn(attr), "Cambria")


def add_header_footer(section):
    section.different_first_page_header_footer = True
    section.header_distance = Inches(0.35)
    section.footer_distance = Inches(0.32)
    header = section.header
    header.is_linked_to_previous = False
    hp = header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    hp.paragraph_format.tab_stops.add_tab_stop(CONTENT_WIDTH, WD_TAB_ALIGNMENT.RIGHT)
    hp.paragraph_format.space_after = Pt(2)
    left = hp.add_run("GOAL AND EVIDENCE CONTINUITY")
    set_run_font(left, "Cambria", 8, bold=True, color=NAVY)
    hp.add_run("\t")
    right = hp.add_run("JAMES PAUL JACKSON")
    set_run_font(right, "Cambria", 8, color=INK)
    add_bottom_border(hp, "12324D", "8")

    first_header = section.first_page_header
    first_header.is_linked_to_previous = False
    first_header.paragraphs[0].text = ""

    def fill_footer(footer):
        footer.is_linked_to_previous = False
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.LEFT
        fp.paragraph_format.tab_stops.add_tab_stop(CONTENT_WIDTH, WD_TAB_ALIGNMENT.RIGHT)
        fp.paragraph_format.space_before = Pt(2)
        add_bottom_border(fp, "FFFFFF", "0")
        pPr = fp._p.get_or_add_pPr()
        pBdr = OxmlElement("w:pBdr")
        top = OxmlElement("w:top")
        top.set(qn("w:val"), "single")
        top.set(qn("w:sz"), "6")
        top.set(qn("w:space"), "1")
        top.set(qn("w:color"), "12324D")
        pBdr.append(top)
        pPr.append(pBdr)
        run = fp.add_run("Pegasus systems white paper  ·  Version 1.1  ·  8 November 2026")
        set_run_font(run, "Cambria", 8, color=INK)
        fp.add_run("\t")
        add_page_field(fp)

    fill_footer(section.footer)
    fill_footer(section.first_page_footer)


def paragraph_format(paragraph, before=0, after=8, keep_next=False, keep_together=False):
    paragraph.paragraph_format.space_before = Pt(before)
    paragraph.paragraph_format.space_after = Pt(after)
    paragraph.paragraph_format.line_spacing = 1.12
    paragraph.paragraph_format.keep_together = keep_together
    paragraph.paragraph_format.keep_with_next = keep_next


def add_equation(document, latex, number):
    table = document.add_table(rows=1, cols=3)
    no_table_borders(table)
    widths = [Inches(0.45), Inches(5.6), Inches(0.45)]
    set_table_widths(table, widths)
    row = table.rows[0]
    prevent_row_split(row)
    left, mid, right = row.cells
    mid.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph_format(mid.paragraphs[0], 2, 2, keep_together=True)
    mid.paragraphs[0]._p.append(omml_from_latex(latex))
    right.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    paragraph_format(right.paragraphs[0], 4, 2)
    run = right.paragraphs[0].add_run(f"({number})")
    set_run_font(run, "Cambria", 11, color=INK)
    spacer = document.add_paragraph()
    paragraph_format(spacer, 0, 4)


def add_image(document, path, alt):
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph_format(paragraph, 6, 2, keep_next=True, keep_together=True)
    run = paragraph.add_run()
    # Width is fixed; height follows the file so the drawing is not stretched.
    from PIL import Image

    with Image.open(path) as image:
        width, height = image.size
    target = Inches(6.3)
    scaled = Emu(int(target) * height / width)
    run.add_picture(str(path), width=target, height=scaled)


def add_caption(document, text, kind):
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT if kind == "table" else WD_ALIGN_PARAGRAPH.LEFT
    paragraph_format(
        paragraph,
        2 if kind == "figure" else 8,
        6 if kind == "figure" else 4,
        keep_next=(kind == "table"),
        keep_together=True,
    )
    add_inline(paragraph, text, size=10, base_italic=True)


def add_code(document, lines):
    table = document.add_table(rows=1, cols=1)
    set_table_widths(table, [CONTENT_WIDTH])
    cell = table.cell(0, 0)
    shade_cell(cell, "F7F7F4")
    set_cell_borders(cell, "D0D0D0", "4")
    prevent_row_split(table.rows[0])
    first = True
    for line in lines:
        paragraph = cell.paragraphs[0] if first else cell.add_paragraph()
        first = False
        paragraph_format(paragraph, 0, 0)
        paragraph.paragraph_format.line_spacing = 1.0
        run = paragraph.add_run(line if line else " ")
        set_run_font(run, "Consolas", 9, color=INK)
    spacer = document.add_paragraph()
    paragraph_format(spacer, 0, 6)


def parse_row(line):
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def is_separator(line):
    return bool(re.fullmatch(r"\|\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?", line.strip()))


def add_data_table(document, rows):
    headers = rows[0]
    body = rows[1:]
    table = document.add_table(rows=1 + len(body), cols=len(headers))
    if len(headers) == 2:
        widths = [Inches(2.15), Inches(4.35)]
    else:
        widths = [CONTENT_WIDTH / len(headers)] * len(headers)
    set_table_widths(table, widths)
    for index, header in enumerate(headers):
        cell = table.rows[0].cells[index]
        shade_cell(cell, "E7EEF6")
        set_cell_borders(cell, "C5CED6", "4")
        paragraph = cell.paragraphs[0]
        paragraph_format(paragraph, 1, 1)
        add_inline(paragraph, header, size=10, base_bold=True, color=NAVY)
    mark_header_row(table.rows[0])
    prevent_row_split(table.rows[0])
    for r_index, row in enumerate(body):
        prevent_row_split(table.rows[r_index + 1])
        for c_index, value in enumerate(row):
            cell = table.rows[r_index + 1].cells[c_index]
            set_cell_borders(cell, "C5CED6", "4")
            if r_index % 2 == 1:
                shade_cell(cell, "F7F8FA")
            paragraph = cell.paragraphs[0]
            paragraph_format(paragraph, 1, 1)
            paragraph.paragraph_format.line_spacing = 1.05
            add_inline(paragraph, value, size=10)
    spacer = document.add_paragraph()
    paragraph_format(spacer, 2, 6)


def render(md_text, document):
    lines = md_text.splitlines()
    i = 0
    title_block = True
    pending_anchor = None
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        anchor = re.fullmatch(r'<a id="([^"]+)"></a>', stripped)
        if anchor:
            pending_anchor = anchor.group(1)
            i += 1
            continue
        if stripped.startswith("$$"):
            i += 1
            math_lines = []
            while i < len(lines) and lines[i].strip() != "$$":
                math_lines.append(lines[i])
                i += 1
            if i < len(lines) and lines[i].strip() == "$$":
                i += 1
            latex, number = extract_tag(" ".join(part.strip() for part in math_lines))
            add_equation(document, latex, number)
            continue
        if stripped.startswith("```"):
            i += 1
            code = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1
            add_code(document, code)
            continue
        if stripped.startswith("!["):
            match = re.fullmatch(r"!\[([^\]]*)\]\(([^)]+)\)", stripped)
            if not match:
                raise ValueError(f"Bad image line: {stripped}")
            alt, rel = match.group(1), match.group(2)
            path = (MD_PATH.parent / rel).resolve()
            add_image(document, path, alt)
            i += 1
            continue
        if stripped.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                if not is_separator(lines[i]):
                    rows.append(parse_row(lines[i]))
                i += 1
            add_data_table(document, rows)
            continue
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            text = stripped[level:].strip()
            if level == 1:
                paragraph = document.add_paragraph()
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                paragraph_format(paragraph, 0, 4, keep_next=True)
                run = paragraph.add_run(text)
                set_run_font(run, "Cambria", 22, bold=True, color=NAVY)
                title_block = True
            else:
                title_block = False
                style = "Heading 1" if level == 2 else "Heading 2"
                paragraph = document.add_paragraph(style=style)
                if pending_anchor:
                    add_bookmark(paragraph, pending_anchor)
                    pending_anchor = None
                add_inline(paragraph, text, size=16 if level == 2 else 13, color=NAVY, base_bold=True)
            i += 1
            continue
        if stripped.startswith("- "):
            items = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                items.append(lines[i].strip()[2:].strip())
                i += 1
            for item in items:
                paragraph = document.add_paragraph()
                paragraph.paragraph_format.left_indent = Inches(0.3)
                paragraph.paragraph_format.first_line_indent = Inches(-0.2)
                paragraph_format(paragraph, 0, 2)
                run = paragraph.add_run("• ")
                set_run_font(run, "Cambria", 11, color=INK)
                add_inline(paragraph, item, size=11)
            continue
        # Paragraph, possibly joined until a blank line.
        buffer = [stripped]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith(("#", "|", "$$", "```", "![", "- ", "<a ")):
            buffer.append(lines[i].strip())
            i += 1
        text = " ".join(buffer)
        paragraph = document.add_paragraph()
        if title_block:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragraph_format(paragraph, 0, 2, keep_next=True)
            if text.startswith("*") and text.endswith("*") and text.count("*") == 2:
                run = paragraph.add_run(text[1:-1])
                set_run_font(run, "Cambria", 13, italic=True, color=NAVY)
            elif text == "James Paul Jackson":
                run = paragraph.add_run(text)
                set_run_font(run, "Cambria", 12, color=INK)
            elif text.startswith("Version "):
                run = paragraph.add_run(text)
                set_run_font(run, "Cambria", 11, color=INK)
                add_bottom_border(paragraph, "12324D", "12")
                paragraph_format(paragraph, 2, 10)
            else:
                add_inline(paragraph, text, size=11)
        elif text.startswith("*Table ") or text.startswith("*Figure "):
            kind = "table" if text.startswith("*Table ") else "figure"
            inner = text[1:-1] if text.endswith("*") else text
            add_caption(document, inner, kind)
            # The paragraph created above is unused; remove it.
            element = paragraph._element
            element.getparent().remove(element)
        elif text.startswith("**Algorithm"):
            paragraph_format(paragraph, 8, 4, keep_next=True, keep_together=True)
            add_inline(paragraph, text, size=11)
        elif text.startswith("**Proposition") or text.startswith("*Proof sketch.*"):
            paragraph_format(paragraph, 6, 6, keep_together=True)
            add_inline(paragraph, text, size=11)
        elif re.match(r"^\[\d+\] ", text):
            paragraph.paragraph_format.left_indent = Inches(0.35)
            paragraph.paragraph_format.first_line_indent = Inches(-0.35)
            paragraph_format(paragraph, 1, 4)
            add_inline(paragraph, text, size=10)
        else:
            paragraph_format(paragraph, 0, 8)
            add_inline(paragraph, text, size=11)
        pending_anchor = None


def build():
    document = Document()
    section = document.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)
    section.top_margin = Inches(0.85)
    section.bottom_margin = Inches(0.7)
    configure_styles(document)
    add_header_footer(section)
    core = document.core_properties
    core.author = "James Paul Jackson"
    core.title = "Goal and Evidence Continuity in Adaptive Agent Swarms"
    core.subject = "Runtime contracts and an evaluation protocol for Pegasus"
    core.category = "Technical report"
    core.comments = "Version 1.1, 8 November 2026."
    render(MD_PATH.read_text(encoding="utf-8"), document)
    DOCX_PATH.parent.mkdir(parents=True, exist_ok=True)
    document.save(DOCX_PATH)
    print(DOCX_PATH)


if __name__ == "__main__":
    try:
        build()
    except Exception as exc:
        print(f"render failed: {exc}", file=sys.stderr)
        raise
