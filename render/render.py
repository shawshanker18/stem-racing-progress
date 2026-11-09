#!/usr/bin/env python3
"""Draws the progress board (README.md + board/*.svg) from progress/part*.json.

Standard library only. Runs in the render workflow; nobody runs it by hand.
"""
import glob
import json
import math
import re
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BG, PANEL, TEXT, MUTED = "#0d1117", "#161b22", "#e6edf3", "#8b949e"
TODO, DONE, FAIL, GOLD, BLUE = "#6e7681", "#2ea043", "#da3633", "#d4a72c", "#388bfd"
FONT = "font-family='Segoe UI,Helvetica,Arial,sans-serif'"

# The board is public: keep code, paths, links and file names out of it.
FORBIDDEN = re.compile(r"`|\bdef |\bimport |https?://|\.(py|json|yml|yaml|stl|npy|npz|csv|md)\b|[A-Za-z]:\\|/[a-z_]+/", re.I)


def load_parts():
    parts = []
    for f in sorted(glob.glob(str(ROOT / "progress" / "part*.json"))):
        p = json.loads(Path(f).read_text(encoding="utf-8"))
        for s in p["sections"]:
            for it in s["items"]:
                it["cells"] = max(1, int(it["cells"]))
                it["done"] = max(0, min(int(it.get("done", 0)), it["cells"]))
                it["failed"] = max(0, min(int(it.get("failed", 0)), it["cells"] - it["done"]))
        check_text(p, Path(f).name)
        parts.append(p)
    if not parts:
        sys.exit("no progress/part*.json files")
    return parts


def check_text(obj, where):
    if isinstance(obj, dict):
        for v in obj.values():
            check_text(v, where)
    elif isinstance(obj, list):
        for v in obj:
            check_text(v, where)
    elif isinstance(obj, str) and FORBIDDEN.search(obj):
        sys.exit(f"{where}: public board text looks like code, a path or a link: {obj!r}")


def count(items):
    c = sum(i["cells"] for i in items)
    return c, sum(i["done"] for i in items), sum(i["failed"] for i in items)


def part_items(p):
    return [i for s in p["sections"] for i in s["items"]]


def pct(d, c):
    return 100.0 * d / c if c else 0.0


# ---------------------------------------------------------------- treemap layout
def squarify(entries, x, y, w, h):
    """entries: [(key, value)] -> [(key, x, y, w, h)], squarified (Bruls et al.)."""
    entries = sorted([e for e in entries if e[1] > 0], key=lambda e: -e[1])
    total = sum(v for _, v in entries)
    if total <= 0 or w <= 0 or h <= 0:
        return []
    scale = w * h / total
    items = [(k, v * scale) for k, v in entries]
    out, row = [], []

    def worst(r, side):
        s = sum(a for _, a in r)
        return max(max(side * side * a / (s * s), (s * s) / (side * side * a)) for _, a in r)

    def place(r, x, y, w, h):
        s = sum(a for _, a in r)
        if w >= h:
            cw, cy = s / h, y
            for k, a in r:
                out.append((k, x, cy, cw, a / cw))
                cy += a / cw
            return x + cw, y, w - cw, h
        rh, cx = s / w, x
        for k, a in r:
            out.append((k, cx, y, a / rh, rh))
            cx += a / rh
        return x, y + rh, w, h - rh

    while items:
        side = min(w, h)
        if not row or worst(row + [items[0]], side) <= worst(row, side):
            row.append(items.pop(0))
        else:
            x, y, w, h = place(row, x, y, w, h)
            row = []
    if row:
        place(row, x, y, w, h)
    return out


# ---------------------------------------------------------------- svg pieces
class Svg:
    def __init__(self, w, h):
        self.w, self.h, self.defs, self.body, self.n = w, h, [], [], 0

    def rect(self, x, y, w, h, fill, extra=""):
        if w > 0 and h > 0:
            self.body.append(f"<rect x='{x:.2f}' y='{y:.2f}' width='{w:.2f}' height='{h:.2f}' fill='{fill}' {extra}/>")

    def text(self, x, y, s, size=12, fill=TEXT, weight="normal", anchor="start", outline=False):
        o = f" stroke='{BG}' stroke-width='3' paint-order='stroke'" if outline else ""
        self.body.append(f"<text x='{x:.1f}' y='{y:.1f}' {FONT} font-size='{size}' font-weight='{weight}' "
                         f"fill='{fill}' text-anchor='{anchor}'{o}>{escape(s)}</text>")

    def grid(self, x, y, s, cols, rows):
        self.n += 1
        pid = f"g{self.n}"
        lw = 0.35 if s < 4 else 0.7
        self.defs.append(f"<pattern id='{pid}' x='{x:.2f}' y='{y:.2f}' width='{s:.3f}' height='{s:.3f}' patternUnits='userSpaceOnUse'>"
                         f"<path d='M {s:.3f} 0 L 0 0 0 {s:.3f}' fill='none' stroke='{BG}' stroke-width='{lw}'/></pattern>")
        self.rect(x, y, cols * s, rows * s, f"url(#{pid})")

    def save(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(
            f"<svg xmlns='http://www.w3.org/2000/svg' width='{self.w}' height='{self.h}' viewBox='0 0 {self.w} {self.h}'>"
            f"<defs>{''.join(self.defs)}</defs><rect width='100%' height='100%' fill='{BG}' rx='6'/>"
            + "".join(self.body) + "</svg>\n", encoding="utf-8")


def cells_box(svg, item, x, y, w, h, label=True):
    """One work item: a block of small squares, green done, red failed, grey to do."""
    pad = 1.0
    x, y, w, h = x + pad, y + pad, w - 2 * pad, h - 2 * pad
    if w < 2 or h < 2:
        return
    svg.rect(x, y, w, h, PANEL)
    n = item["cells"]
    s = math.sqrt(w * h / n)
    while s > 1.2 and math.floor(w / s) * math.floor(h / s) < n:
        s *= 0.97
    cols = max(1, math.floor(w / s))
    rows = math.ceil(n / cols)
    if rows * s > h:            # too many to draw one by one: shrink the grid to fit
        s = h / rows
    def fill(a, b, colour):
        if b <= a:
            return
        r0, c0 = divmod(a, cols)
        r1, c1 = divmod(b, cols)
        if r0 == r1:
            svg.rect(x + c0 * s, y + r0 * s, (c1 - c0) * s, s, colour)
            return
        svg.rect(x + c0 * s, y + r0 * s, (cols - c0) * s, s, colour)
        svg.rect(x, y + (r0 + 1) * s, cols * s, (r1 - r0 - 1) * s, colour)
        svg.rect(x, y + r1 * s, c1 * s, s, colour)
    fill(0, n, TODO)
    fill(0, item["done"], DONE)
    fill(item["done"], item["done"] + item["failed"], FAIL)
    if s >= 2.2:
        svg.grid(x, y, s, cols, rows)
    if label and w > 34 and h > 14:
        name = item["name"]
        room = int((w - 6) / 6.3)
        if len(name) > room:
            name = name[: max(1, room - 1)] + "…"
        svg.text(x + 3, y + 11, name, size=10.5, weight="bold", outline=True)


def treemap(svg, groups, x, y, w, h, header=14):
    """groups: [(title, items)]: one framed block per group, its items squarified inside."""
    for (title, items), gx, gy, gw, gh in squarify([((t, it), count(it)[0]) for t, it in groups], x, y, w, h):
        svg.rect(gx + 1, gy + 1, gw - 2, gh - 2, "none", f"stroke='{MUTED}' stroke-opacity='0.35'")
        top = header if gh > 3 * header and gw > 60 else 0
        if top:
            c, d, _ = count(items)
            svg.text(gx + 4, gy + 11, f"{title} · {pct(d, c):.0f}%", size=10.5, fill=MUTED, weight="bold")
        for it, ix, iy, iw, ih in squarify([(i, i["cells"]) for i in items], gx + 2, gy + 2 + top, gw - 4, gh - 4 - top):
            cells_box(svg, it, ix, iy, iw, ih)


def bar(svg, x, y, w, h, c, d, f):
    svg.rect(x, y, w, h, TODO)
    svg.rect(x, y, w * d / c if c else 0, h, DONE)
    svg.rect(x + (w * d / c if c else 0), y, w * f / c if c else 0, h, FAIL)


# ---------------------------------------------------------------- the board
def header_svg(parts):
    allc, alld, allf = count([i for p in parts for i in part_items(p)])
    done_parts = sum(1 for p in parts if p.get("status") == "done")
    updated = max(p.get("updated", "") for p in parts)
    pills = [("overall", f"{pct(alld, allc):.1f}%", GOLD), ("squares done", f"{alld:,}/{allc:,}", DONE),
             ("parts signed off", f"{done_parts}/{len(parts)}", BLUE), ("updated", updated, "#30363d")]
    svg, x = Svg(900, 40), 8
    for k, v, colour in pills:
        kw, vw = 14 + 7.2 * len(k), 14 + 7.2 * len(v)
        svg.rect(x, 8, kw, 24, "#30363d")
        svg.rect(x + kw, 8, vw, 24, colour)
        svg.text(x + kw / 2, 25, k, size=13, anchor="middle")
        svg.text(x + kw + vw / 2, 25, v, size=13, anchor="middle", fill="#0d1117" if colour in (GOLD, DONE) else TEXT)
        x += kw + vw + 10
    svg.save(ROOT / "board" / "header.svg")


def overview_svg(parts):
    W, H = 900, 520
    svg = Svg(W, H)
    allc, alld, _ = count([i for p in parts for i in part_items(p)])
    svg.text(8, 22, f"Whole project: {pct(alld, allc):.1f}% ({alld:,}/{allc:,} squares)", size=15, weight="bold")
    treemap(svg, [(f"Part {p['part']} {p['name']}", part_items(p)) for p in parts], 6, 32, W - 12, 300)
    y = 352
    svg.text(8, y, "Progress by part", size=15, weight="bold")
    for p in parts:
        y += 24
        c, d, f = count(part_items(p))
        svg.text(8, y + 10, f"Part {p['part']}: {p['name']}", size=12, weight="bold")
        bar(svg, 230, y, 520, 13, c, d, f)
        svg.text(W - 10, y + 11, f"{pct(d, c):.1f}%", size=12, anchor="end")
    y += 30
    x = 8
    for k, colour in (("done", DONE), ("failed, being redone", FAIL), ("still to do", TODO)):
        svg.rect(x, y, 12, 12, colour)
        svg.text(x + 18, y + 10, k, size=11, fill=MUTED)
        x += 40 + 6.5 * len(k)
    svg.h = y + 24
    svg.save(ROOT / "board" / "overview.svg")


def part_svg(p):
    W = 900
    sections = p["sections"]
    H = 400 + 22 * len(sections) + 30
    svg = Svg(W, H)
    c, d, f = count(part_items(p))
    svg.text(8, 22, f"Part {p['part']}: {p['name']}: {pct(d, c):.1f}% ({d:,}/{c:,})", size=15, weight="bold")
    treemap(svg, [(s["name"], s["items"]) for s in sections], 6, 32, W - 12, 360)
    y = 410
    svg.text(8, y, "By stage", size=14, weight="bold")
    for s in sections:
        y += 22
        sc, sd, sf = count(s["items"])
        svg.text(8, y + 10, s["name"], size=12)
        bar(svg, 300, y, 450, 12, sc, sd, sf)
        svg.text(W - 10, y + 10, f"{sd:,}/{sc:,}", size=12, anchor="end")
    svg.h = y + 24
    svg.save(ROOT / "board" / f"part{p['part']}.svg")


def readme(parts):
    out = [
        "# STEM Racing car: progress board",
        "",
        "Our team is building, part by part, a computer system that designs the fastest legal car for the "
        "STEM Racing 20 m race. This board shows how far each part has come. It holds **no code and no design "
        "data**, only progress.",
        "",
        "Each small square is one piece of work or one test case. **Green** = done, **red** = failed and being "
        "redone, **grey** = still to do. Each part's own builder updates its file after every step, and the "
        "pictures redraw themselves.",
        "",
        "![summary](board/header.svg)",
        "",
        "![all parts](board/overview.svg)",
        "",
    ]
    for p in parts:
        c, d, _ = count(part_items(p))
        status = {"done": "Signed off", "active": "Being built", "waiting": "Waiting to start"}.get(p.get("status"), "Being built")
        out += [f"## Part {p['part']}: {p['name']}", "", f"*{p['tagline']}*", "",
                f"**Status:** {status} · **{pct(d, c):.1f}%** · updated {p.get('updated', '')}", "",
                "**What it does**", ""]
        out += [f"- {line}" for line in p["what"]]
        out += ["", f"![part {p['part']}](board/part{p['part']}.svg)", "", f"**Now:** {p.get('now', '')}", ""]
        log = p.get("log", [])[-6:]
        if log:
            out += ["**Recent steps**", ""] + [f"- {e['date']}: {e['text']}" for e in reversed(log)] + [""]
    out += ["---", "", "*This board is drawn automatically from each part's progress file.*", ""]
    (ROOT / "README.md").write_text("\n".join(out), encoding="utf-8")


def main():
    parts = load_parts()
    header_svg(parts)
    overview_svg(parts)
    for p in parts:
        part_svg(p)
    readme(parts)
    print("board drawn:", ", ".join(f"part {p['part']}" for p in parts))


if __name__ == "__main__":
    main()
