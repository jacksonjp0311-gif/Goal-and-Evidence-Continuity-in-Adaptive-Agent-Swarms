"""Draw the two schematic figures used by the white paper."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "figures"
FONT = Path(r"C:\Windows\Fonts\segoeui.ttf")
FONT_B = Path(r"C:\Windows\Fonts\segoeuib.ttf")


def font(size, bold=False):
    return ImageFont.truetype(str(FONT_B if bold else FONT), size)


def wrap(draw, text, face, width):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=face) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def box(draw, xy, title, lines, fill, title_font, body_font, ink="#1c1c1c"):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle(xy, radius=12, fill=fill, outline="#1c1c1c", width=2)
    draw.text((x0 + 16, y0 + 12), title, font=title_font, fill="#12324d")
    y = y0 + 44
    for line in lines:
        draw.text((x0 + 16, y), line, font=body_font, fill=ink)
        y += 24
    return xy


def arrow(draw, start, end, label=None, label_font=None):
    draw.line([start, end], fill="#1c1c1c", width=2)
    x0, y0 = start
    x1, y1 = end
    if abs(x1 - x0) >= abs(y1 - y0):
        sign = 1 if x1 >= x0 else -1
        head = [(x1, y1), (x1 - 12 * sign, y1 - 6), (x1 - 12 * sign, y1 + 6)]
    else:
        sign = 1 if y1 >= y0 else -1
        head = [(x1, y1), (x1 - 6, y1 - 12 * sign), (x1 + 6, y1 - 12 * sign)]
    draw.polygon(head, fill="#1c1c1c")
    if label and label_font:
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        tw = draw.textlength(label, font=label_font)
        draw.text((mx - tw / 2, my - 22), label, font=label_font, fill="#333333")


def figure_one(path):
    image = Image.new("RGB", (1500, 860), "white")
    draw = ImageDraw.Draw(image)
    title = font(22, True)
    body = font(16)
    small = font(15)
    label = font(14)
    draw.text((40, 24), "State transaction", font=title, fill="#12324d")
    box(draw, (40, 80, 390, 250), "Agents", [
        "Replaceable executors.",
        "Propose work.",
        "Submit observations.",
        "Do not commit success.",
    ], "#f4f7fb", font(18, True), body)
    box(draw, (560, 70, 980, 270), "Acceptance kernel", [
        "Authorizes transitions.",
        "Checks revision, epoch,",
        "contract, and snapshot.",
        "Accepts or rejects claims.",
    ], "#e7eef6", font(18, True), body)
    box(draw, (1100, 70, 1460, 270), "Durable mission state", [
        "Contract and graph.",
        "Snapshot and evidence.",
        "Ownership epochs.",
        "Effect and resource ledgers.",
    ], "#f7f7f4", font(18, True), body)
    arrow(draw, (390, 140), (560, 140), "proposals", label)
    arrow(draw, (560, 190), (390, 190), "decisions", label)
    arrow(draw, (980, 160), (1100, 160), "commit", label)

    draw.rounded_rectangle((40, 330, 1460, 820), radius=14, outline="#8a6a32", width=2)
    draw.text((60, 346), "Outside the state transaction", font=title, fill="#6b5018")
    box(draw, (60, 410, 470, 610), "Scheduler", [
        "Ready work and reservations.",
        "Separate resource classes.",
        "Admission is not acceptance.",
    ], "#fbf6ea", font(18, True), body)
    box(draw, (540, 410, 980, 610), "Model execution", [
        "Local or cloud providers.",
        "Immutable attempt settings.",
        "Returns usage and output.",
    ], "#fbf6ea", font(18, True), body)
    box(draw, (1050, 410, 1440, 610), "Tool execution", [
        "Authorized capabilities.",
        "May have external effects.",
        "Returns a receipt or unknown.",
    ], "#fbf6ea", font(18, True), body)
    arrow(draw, (770, 270), (770, 410), "admit work", label)
    arrow(draw, (470, 480), (540, 480), "reserve", label)
    arrow(draw, (980, 500), (1050, 500), "call", label)
    note = "Receipts return to the kernel for reconciliation. They do not rewrite accepted state by themselves."
    for i, line in enumerate(wrap(draw, note, small, 1360)):
        draw.text((60, 660 + i * 26), line, font=small, fill="#1c1c1c")
    image.save(path, "PNG")


def figure_two(path):
    image = Image.new("RGB", (1500, 620), "white")
    draw = ImageDraw.Draw(image)
    title = font(20, True)
    body = font(16)
    label = font(15)
    box(draw, (40, 24, 460, 230), "Snapshot A", [
        "Selected deliverable A.",
        "Test result T-A recorded.",
        "Subjects match A.",
        "Current discharge: applicable.",
    ], "#eef6ee", title, body)
    box(draw, (540, 24, 960, 230), "Selection changes", [
        "Kernel selects snapshot B.",
        "T-A remains in history.",
        "It is not deleted.",
        "It no longer supports B.",
    ], "#f7f7f4", title, body)
    box(draw, (1040, 24, 1460, 230), "Snapshot B", [
        "Selected deliverable B.",
        "Affected discharge invalidated.",
        "B needs applicable evidence.",
        "Success is not inherited.",
    ], "#f8eeee", title, body)
    arrow(draw, (460, 120), (540, 120))
    arrow(draw, (960, 120), (1040, 120))
    draw.text((468, 78), "select B", font=label, fill="#333333")
    draw.rounded_rectangle((40, 268, 1460, 580), radius=14, fill="#f7f7fb", outline="#1c1c1c", width=2)
    draw.text((64, 292), "Unrelated evidence", font=title, fill="#12324d")
    lines = [
        "Evidence whose declared dependencies are unchanged can remain applicable.",
        "A content hash identifies an artifact. It does not establish that a claim is still true.",
        "Policy changes, expired external observations, and changed dependencies",
        "invalidate affected current discharges in the same way as selecting B.",
    ]
    y = 340
    for line in lines:
        draw.text((64, y), line, font=body, fill="#1c1c1c")
        y += 36
    image.save(path, "PNG")


def svg_text(x, y, text, size=16, weight="400", fill="#1c1c1c"):
    escaped = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    return (
        f'<text x="{x}" y="{y}" font-family="Segoe UI, Arial, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" fill="{fill}">{escaped}</text>'
    )


def svg_box(x, y, w, h, title, lines, fill):
    parts = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" stroke="#1c1c1c" stroke-width="2"/>',
        svg_text(x + 16, y + 32, title, 18, "700", "#12324d"),
    ]
    yy = y + 62
    for line in lines:
        parts.append(svg_text(x + 16, yy, line, 16, "400", "#1c1c1c"))
        yy += 26
    return "\n".join(parts)


def svg_arrow(x1, y1, x2, y2):
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#1c1c1c" stroke-width="2" '
        f'marker-end="url(#arrow)"/>'
    )


def svg_document(width, height, body):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="#ffffff"/>
<defs>
  <marker id="arrow" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto">
    <polygon points="0 0, 10 4, 0 8" fill="#1c1c1c"/>
  </marker>
</defs>
{body}
</svg>
'''


def figure_one_svg(path):
    parts = [
        svg_text(40, 48, "State transaction", 22, "700", "#12324d"),
        svg_box(40, 80, 350, 180, "Agents", [
            "Replaceable executors.",
            "Propose work.",
            "Submit observations.",
            "Do not commit success.",
        ], "#f4f7fb"),
        svg_box(560, 70, 420, 210, "Acceptance kernel", [
            "Authorizes transitions.",
            "Checks revision, epoch,",
            "contract, and snapshot.",
            "Accepts or rejects claims.",
        ], "#e7eef6"),
        svg_box(1100, 70, 360, 210, "Durable mission state", [
            "Contract and graph.",
            "Snapshot and evidence.",
            "Ownership epochs.",
            "Effect and resource ledgers.",
        ], "#f7f7f4"),
        svg_arrow(390, 140, 555, 140),
        svg_text(410, 128, "proposals", 14, "400", "#333333"),
        svg_arrow(555, 190, 390, 190),
        svg_text(410, 208, "decisions", 14, "400", "#333333"),
        svg_arrow(980, 160, 1095, 160),
        svg_text(990, 148, "commit", 14, "400", "#333333"),
        '<rect x="40" y="330" width="1420" height="490" rx="14" fill="#ffffff" stroke="#8a6a32" stroke-width="2"/>',
        svg_text(60, 372, "Outside the state transaction", 22, "700", "#6b5018"),
        svg_box(60, 410, 410, 190, "Scheduler", [
            "Ready work and reservations.",
            "Separate resource classes.",
            "Admission is not acceptance.",
        ], "#fbf6ea"),
        svg_box(540, 410, 440, 190, "Model execution", [
            "Local or cloud providers.",
            "Immutable attempt settings.",
            "Returns usage and output.",
        ], "#fbf6ea"),
        svg_box(1050, 410, 390, 190, "Tool execution", [
            "Authorized capabilities.",
            "May have external effects.",
            "Returns a receipt or unknown.",
        ], "#fbf6ea"),
        svg_arrow(770, 280, 770, 405),
        svg_text(784, 350, "admit work", 14, "400", "#333333"),
        svg_arrow(470, 500, 535, 500),
        svg_text(476, 488, "reserve", 14, "400", "#333333"),
        svg_arrow(980, 520, 1045, 520),
        svg_text(986, 508, "call", 14, "400", "#333333"),
        svg_text(60, 680, "Receipts return to the kernel for reconciliation.", 16, "400", "#1c1c1c"),
        svg_text(60, 710, "They do not rewrite accepted state by themselves.", 16, "400", "#1c1c1c"),
    ]
    path.write_text(svg_document(1500, 860, "\n".join(parts)), encoding="utf-8")


def figure_two_svg(path):
    parts = [
        svg_box(40, 24, 420, 206, "Snapshot A", [
            "Selected deliverable A.",
            "Test result T-A recorded.",
            "Subjects match A.",
            "Current discharge: applicable.",
        ], "#eef6ee"),
        svg_box(540, 24, 420, 206, "Selection changes", [
            "Kernel selects snapshot B.",
            "T-A remains in history.",
            "It is not deleted.",
            "It no longer supports B.",
        ], "#f7f7f4"),
        svg_box(1040, 24, 420, 206, "Snapshot B", [
            "Selected deliverable B.",
            "Affected discharge invalidated.",
            "B needs applicable evidence.",
            "Success is not inherited.",
        ], "#f8eeee"),
        svg_arrow(460, 120, 535, 120),
        svg_text(468, 100, "select B", 14, "400", "#333333"),
        svg_arrow(960, 120, 1035, 120),
        '<rect x="40" y="268" width="1420" height="312" rx="14" fill="#f7f7fb" stroke="#1c1c1c" stroke-width="2"/>',
        svg_text(64, 312, "Unrelated evidence", 20, "700", "#12324d"),
        svg_text(64, 360, "Evidence whose declared dependencies are unchanged can remain applicable.", 16, "400", "#1c1c1c"),
        svg_text(64, 396, "A content hash identifies an artifact. It does not establish that a claim is still true.", 16, "400", "#1c1c1c"),
        svg_text(64, 432, "Policy changes, expired external observations, and changed dependencies", 16, "400", "#1c1c1c"),
        svg_text(64, 468, "invalidate affected current discharges in the same way as selecting B.", 16, "400", "#1c1c1c"),
    ]
    path.write_text(svg_document(1500, 620, "\n".join(parts)), encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    figure_one(OUT / "figure-1.png")
    figure_two(OUT / "figure-2.png")
    figure_one_svg(OUT / "figure-1.svg")
    figure_two_svg(OUT / "figure-2.svg")
    print(OUT / "figure-1.png")
    print(OUT / "figure-2.png")


if __name__ == "__main__":
    main()
