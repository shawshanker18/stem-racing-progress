#!/usr/bin/env python3
"""Draws the progress board from progress/part*.json.

Writes README.md, board/*.svg (badges and the progress map), board/history.json and
site/ (progress.html, history.html) for GitHub Pages. Standard library only. Runs in the
render workflow; nobody runs it by hand.
"""
import datetime
import glob
import json
import re
import sys
import textwrap
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOARD, SITE = ROOT / "board", ROOT / "site"
SITE_URL = "https://shawshanker18.github.io/stem-racing-progress"

PANEL_W, GAP, MAP_H, HEADER = 495, 10, 300, 30
WIDTH = 2 * PANEL_W + GAP
BG, TEXT, MUTED = "#0d1117", "#ffffff", "#8b949e"
DONE, TODO, FAIL = "#2ea043", "#6e7681", "#da3633"
LABEL_W, COUNT_W, ROW = 150, 70, 20

# The board is public: keep code, paths, links and file names out of it.
FORBIDDEN = re.compile(r"`|\bdef |\bimport |https?://|\.(py|json|yml|yaml|stl|npy|npz|csv|md)\b|[A-Za-z]:\\|/[a-z_]+/", re.I)


# ------------------------------------------------------------------ data
def load_parts():
    parts = []
    for f in sorted(glob.glob(str(ROOT / "progress" / "part*.json"))):
        p = json.loads(Path(f).read_text(encoding="utf-8"))
        for s in p["sections"]:
            for it in s["items"]:
                it["cells"] = max(1, int(it["cells"]))
                it["done"] = max(0, min(int(it.get("done", 0)), it["cells"]))
                it["failed"] = max(0, min(int(it.get("failed", 0)), it["cells"] - it["done"]))
                it["part"], it["section"] = p["part"], s["name"]
        check_text(p, Path(f).name)
        parts.append(p)
    if not parts:
        sys.exit("no progress files")
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


def items(parts, tests=None):
    out = []
    for p in parts:
        for s in p["sections"]:
            is_test = s["name"].lower().startswith("test")
            if tests is None or tests == is_test:
                out += s["items"]
    return out


def tally(its):
    c = sum(i["cells"] for i in its)
    d = sum(i["done"] for i in its)
    return {"total": c, "done": d, "failed": sum(i["failed"] for i in its),
            "percent": round(100 * d / c, 1) if c else 0.0}


# ------------------------------------------------------------------ layout
def squarify(values, x, y, w, h):
    """Squarified treemap: rectangles for values (largest first), filling (x, y, w, h)."""
    total = sum(values)
    areas = [v * w * h / total for v in values]
    rects, row = [], []

    def worst(r, side):
        s = sum(r)
        return max(max(side * side * a / (s * s), (s * s) / (side * side * a)) for a in r)

    def lay(r, x, y, w, h):
        thick = sum(r) / min(w, h)
        off = 0.0
        for a in r:
            length = a / thick
            rects.append((x, y + off, thick, length) if w >= h else (x + off, y, length, thick))
            off += length
        return (x + thick, y, w - thick, h) if w >= h else (x, y + thick, w, h - thick)

    while areas:
        side = min(w, h)
        if not row or worst(row + [areas[0]], side) <= worst(row, side):
            row.append(areas.pop(0))
        else:
            x, y, w, h = lay(row, x, y, w, h)
            row = []
    if row:
        lay(row, x, y, w, h)
    return rects


def grid_cells(n, x, y, w, h):
    """n cells that exactly fill the box: near-square rows, cells stretched to fit each row."""
    if n <= 0 or w <= 0 or h <= 0:
        return []
    rows = max(1, min(n, round((n * h / w) ** 0.5)))
    out = []
    for r in range(rows):
        k = n // rows + (1 if r < n % rows else 0)
        cw, ch = w / k, h / rows
        out += [(x + c * cw, y + r * ch, cw, ch) for c in range(k)]
    return out


# ------------------------------------------------------------------ svg helpers
def rect(x, y, w, h, fill, stroke=0.5):
    return (f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}" '
            f'stroke="{BG}" stroke-width="{stroke}"/>')


def label(x, y, s, size=12, anchor="start", fill=TEXT, weight="normal"):
    return (f'<text x="{x:.2f}" y="{y:.2f}" font-family="sans-serif" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}" stroke="{BG}" stroke-width="3" paint-order="stroke">{escape(s)}</text>')


def short(it):
    return f"{it['part']} {it.get('short') or it['name']}"


def treemap(title, its, left):
    t = tally(its)
    out = [label(left + 4, 21, f"{title}: {t['percent']}% ({t['done']:,}/{t['total']:,})", 16)]
    its = sorted(its, key=lambda i: -i["cells"])
    for it, (x, y, w, h) in zip(its, squarify([i["cells"] for i in its], left, HEADER, PANEL_W, MAP_H)):
        failed = f', {it["failed"]} failed' if it["failed"] else ""
        out.append(f'<g><title>Part {it["part"]}, {escape(it["section"])}: {escape(it["name"])}: '
                   f'{it["done"]}/{it["cells"]} done{failed}</title>')
        for k, cell in enumerate(grid_cells(it["cells"], x + 1, y + 1, w - 2, h - 2)):
            colour = DONE if k < it["done"] else FAIL if k < it["done"] + it["failed"] else TODO
            out.append(rect(*cell, colour))
        out.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="none" stroke="{BG}" stroke-width="2"/>')
        room = int((w - 8) / 6.6)
        bare = it.get("short") or it["name"]
        fit = next((s for s in (short(it), bare) if len(s) <= room), None)
        if fit is None and room >= 6:
            fit = bare[:room]
        if fit and h > 22:
            out.append(label(x + 4, y + 15, fit))
        out.append("</g>")
    return out


def bar_row(x, y, name, done, failed, total, caption):
    track = PANEL_W - LABEL_W - COUNT_W - 8
    left = x + LABEL_W
    out = [label(x, y + 11, name, 12), f'<rect x="{left}" y="{y}" width="{track}" height="14" fill="{TODO}"/>']
    if total:
        if done:
            out.append(f'<rect x="{left}" y="{y}" width="{max(track * done / total, 1):.2f}" height="14" fill="{DONE}"/>')
        if failed:
            out.append(f'<rect x="{left + track * done / total:.2f}" y="{y}" width="{max(track * failed / total, 1):.2f}" height="14" fill="{FAIL}"/>')
    out.append(label(x + PANEL_W - 4, y + 11, caption, 12, anchor="end"))
    return out


def progress_svg(parts):
    out = treemap("Work done", items(parts, tests=False), 0)
    out += treemap("Tests passed", items(parts, tests=True), PANEL_W + GAP)
    y0 = HEADER + MAP_H + 34
    out.append(label(4, y0, "Progress by part", 16))
    y = y0 + 14
    for p in parts:
        t = tally(items([p]))
        out += bar_row(4, y, f"{p['part']} {p['name']}", t["done"], t["failed"], t["total"], f"{t['percent']}%")
        y += ROW
    y += 18
    out.append(label(4, y, "Tests passed by part", 16))
    y += 14
    for p in parts:
        t = tally(items([p], tests=True))
        out += bar_row(4, y, f"{p['part']} {p['name']}", t["done"], t["failed"], t["total"], f"{t['done']:,}/{t['total']:,}")
        y += ROW
    left_end = y
    x, y = PANEL_W + GAP, y0
    out.append(label(x, y, "Now", 16))
    y += 20
    for p in parts:
        out.append(label(x, y, f"{p['part']} {p['name']}", 12, weight="bold"))
        y += 16
        for line in textwrap.wrap(p.get("now", ""), 78)[:3]:
            out.append(label(x + 8, y, line, 12, fill="#d0d7de"))
            y += 16
        y += 6
    height = max(left_end, y) + 26
    out.append(label(4, height - 10, "Each square is one piece of work or one test case. Green: done. Red: failed, being redone. Grey: still to do. "
                     "Counted from each part's progress file.", 11, fill=MUTED))
    return "\n".join([f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" width="{WIDTH}" height="{height}">',
                      rect(0, 0, WIDTH, height, BG, 0), *out, "</svg>"]) + "\n"


def badge(name, value, colour):
    left, right = 10 + 7 * len(name), 10 + 7 * len(value)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{left + right}" height="20" role="img" aria-label="{escape(name)}: {escape(value)}">'
            f'<rect width="{left}" height="20" fill="#555"/><rect x="{left}" width="{right}" height="20" fill="{colour}"/>'
            f'<g fill="#fff" font-family="Verdana,DejaVu Sans,sans-serif" font-size="11" text-anchor="middle">'
            f'<text x="{left / 2}" y="14">{escape(name)}</text><text x="{left + right / 2}" y="14">{escape(value)}</text></g></svg>\n')


def scale_colour(pct):
    return "#4c1" if pct >= 90 else "#97ca00" if pct >= 60 else "#dfb317" if pct >= 30 else "#fe7d37"


# ------------------------------------------------------------------ outputs
def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


# ------------------------------------------------------------------ timelines (task sheets)
TASK_STYLE = {"done": ("#2ea043", "Done", "✅"), "doing": ("#388bfd", "Working on it", "🔄"),
              "failed": ("#da3633", "Failed, being redone", "❌"), "blocked": ("#d29922", "Blocked", "⏸️"),
              "todo": ("#30363d", "To do", "⬜")}


def task_list(p):
    out = []
    for k in p.get("tasks", []):
        s = k.get("status", "todo")
        if s not in TASK_STYLE:
            sys.exit(f"part {p['part']}: task status must be one of {list(TASK_STYLE)}, got {s!r}")
        out.append(k)
    return out


def task_tally(p):
    ts = task_list(p)
    return sum(1 for k in ts if k["status"] == "done"), len(ts)


def timeline_svg(parts):
    left, row_h, top = 210, 58, 34
    H = top + row_h * len(parts) + 40
    out = [label(8, 22, "Timelines: each part's steps in order", 16)]
    y = top
    for p in parts:
        ts = task_list(p)
        d, n = task_tally(p)
        out.append(label(8, y + 20, f"{p['part']} {p['name']}", 13, weight="bold"))
        out.append(label(8, y + 38, f"{d}/{n} steps done" + (" · waiting to start" if p.get("status") == "waiting" else ""), 11, fill=MUTED))
        if ts:
            gap = 4
            bw = (WIDTH - left - 8 - gap * (len(ts) - 1)) / len(ts)
            for i, k in enumerate(ts):
                x = left + i * (bw + gap)
                colour = TASK_STYLE[k["status"]][0]
                out.append(f'<g><title>{i + 1}. {escape(k["title"])}: {TASK_STYLE[k["status"]][1]}</title>'
                           f'<rect x="{x:.2f}" y="{y + 4:.2f}" width="{bw:.2f}" height="{row_h - 14}" rx="4" fill="{colour}" '
                           f'stroke="#6e7681" stroke-width="{0.8 if k["status"] == "todo" else 0}"/>')
                lab = f'{i + 1}. ' + (k.get("short") or k["title"])
                room = max(1, int((bw - 6) / 5.6))
                lines, cur = [], ""
                for w_ in lab.split():
                    if len(cur) + len(w_) + (1 if cur else 0) <= room:
                        cur = f"{cur} {w_}".strip()
                    else:
                        if cur:
                            lines.append(cur)
                        cur = w_[:room]
                if cur:
                    lines.append(cur)
                for j, line in enumerate(lines[:3]):
                    out.append(label(x + bw / 2, y + 19 + j * 12, line, 9.5, anchor="middle"))
                out.append("</g>")
        y += row_h
    x = left
    for key in ("done", "doing", "failed", "blocked", "todo"):
        colour, name, _ = TASK_STYLE[key]
        out.append(f'<rect x="{x}" y="{y + 6}" width="12" height="12" fill="{colour}" stroke="#6e7681" stroke-width="0.8"/>')
        out.append(label(x + 18, y + 16, name, 11, fill=MUTED))
        x += 30 + 6.5 * len(name)
    return "\n".join([f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {H}" width="{WIDTH}" height="{H}">',
                      rect(0, 0, WIDTH, H, BG, 0), *out, "</svg>"]) + "\n"


def task_table_md(p):
    ts = task_list(p)
    if not ts:
        return []
    out = ["| # | Step | Status | Started | Finished | Note |", "|---|---|---|---|---|---|"]
    for i, k in enumerate(ts, 1):
        _, name, icon = TASK_STYLE[k["status"]]
        out.append(f"| {i} | {k['title']} | {icon} {name} | {k.get('started', '')} | {k.get('finished', '')} | {k.get('note', '')} |")
    return out + [""]


def task_table_html(p):
    ts = task_list(p)
    if not ts:
        return ""
    rows = "".join(f"<tr><td>{i}</td><td>{escape(k['title'])}</td><td>{TASK_STYLE[k['status']][2]} {TASK_STYLE[k['status']][1]}</td>"
                   f"<td>{escape(k.get('started', ''))}</td><td>{escape(k.get('finished', ''))}</td><td>{escape(k.get('note', ''))}</td></tr>"
                   for i, k in enumerate(ts, 1))
    return ("<table><tr><th>#</th><th>Step</th><th>Status</th><th>Started</th><th>Finished</th><th>Note</th></tr>"
            + rows + "</table>")


def update_history(parts):
    path = BOARD / "history.json"
    hist = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    today = datetime.date.today().isoformat()
    entry = {"date": today, "overall": tally(items(parts))["percent"], "tests": tally(items(parts, tests=True))["percent"],
             "parts": {str(p["part"]): tally(items([p]))["percent"] for p in parts}}
    hist = [h for h in hist if h["date"] != today] + [entry]
    write(path, json.dumps(hist, indent=1) + "\n")
    return hist


def readme(parts, overall, tests, signed):
    out = [
        "# STEM Racing car: progress",
        "",
        "Our team is building, part by part, a computer system that designs the fastest legal car for the "
        "STEM Racing 20 m race. This page shows how far each part has come. It holds **no code and no design "
        "data**, only progress.",
        "",
        "## Status",
        "",
        f"[![overall](board/badge-overall.svg)]({SITE_URL}/progress.html) "
        f"[![tests passed](board/badge-tests.svg)]({SITE_URL}/progress.html) "
        f"[![parts signed off](board/badge-parts.svg)]({SITE_URL}/progress.html) "
        f"[![updated](board/badge-updated.svg)]({SITE_URL}/history.html)",
        "",
        "[![timelines](board/timeline.svg)](#the-five-parts)",
        "",
        f"[![progress map](board/progress.svg)]({SITE_URL}/progress.html)",
        "",
        f"[Full progress, part by part]({SITE_URL}/progress.html) · [Progress history]({SITE_URL}/history.html)",
        "",
        "<sub>Each square is one piece of work or one test case, counted from each part's progress file. "
        "\"Groundwork\" is work finished before this phase. Each part's builder updates its own file after every step.</sub>",
        "",
        "## The five parts",
        "",
    ]
    for p in parts:
        t = tally(items([p]))
        status = {"done": "signed off", "active": "being built", "waiting": "waiting to start"}.get(p.get("status"), "being built")
        out += [f"### {p['part']}. {p['name']}", "", f"*{p['tagline']}* {t['percent']}% · {status}", ""]
        out += [f"- {line}" for line in p["what"]]
        out += ["", f"**Now:** {p.get('now', '')}", ""]
        d, n = task_tally(p)
        if n:
            out += [f"**Timeline:** {d} of {n} steps done", ""] + task_table_md(p)
    out += ["---", "", "*Drawn automatically from the progress files. Nothing here can be used to rebuild the work.*", ""]
    return "\n".join(out)


PAGE_HEAD = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
             '<meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title><style>'
             'body{{font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;max-width:1040px;margin:auto;padding:16px;'
             'background:#0d1117;color:#e6edf3}}a{{color:#58a6ff}}svg{{max-width:100%;height:auto}}'
             'table{{border-collapse:collapse;width:100%;margin:8px 0 20px}}th,td{{border-bottom:1px solid #30363d;padding:4px 8px;text-align:left}}'
             'td.n{{text-align:right;white-space:nowrap}}.bar{{background:#6e7681;height:12px;min-width:120px;display:flex}}'
             '.bar i{{display:block;height:12px}}.muted{{color:#8b949e}}h2{{border-bottom:1px solid #30363d;padding-bottom:4px;margin-top:32px}}'
             '</style></head><body>')


def bar_html(it):
    d, f, c = it["done"], it["failed"], it["cells"]
    return (f'<div class="bar"><i style="width:{100 * d / c:.2f}%;background:{DONE}"></i>'
            f'<i style="width:{100 * f / c:.2f}%;background:{FAIL}"></i></div>')


def progress_page(parts, svg, badges, tl_svg=''):
    out = [PAGE_HEAD.format(title="STEM Racing car: progress"),
           "<h1>STEM Racing car: progress</h1>",
           " ".join(f'<img src="{b}" alt="">' for b in badges),
           f"<p>{tl_svg}</p>",
           f"<p>{svg}</p>",
           '<p><a href="history.html">Progress history</a> · <a href="https://github.com/shawshanker18/stem-racing-progress">Repository</a></p>']
    for p in parts:
        t = tally(items([p]))
        out += [f'<h2 id="part{p["part"]}">{p["part"]}. {escape(p["name"])} <span class="muted">{t["percent"]}%</span></h2>',
                f'<p><i>{escape(p["tagline"])}</i></p><ul>' + "".join(f"<li>{escape(x)}</li>" for x in p["what"]) + "</ul>",
                f'<p><b>Now:</b> {escape(p.get("now", ""))}</p>', task_table_html(p)]
        for s in p["sections"]:
            st = tally(s["items"])
            out.append(f'<table><tr><th>{escape(s["name"])}</th><th style="width:45%"></th><th class="n">{st["done"]:,}/{st["total"]:,}</th></tr>')
            for it in s["items"]:
                extra = f', {it["failed"]} failed' if it["failed"] else ""
                out.append(f'<tr><td>{escape(it["name"])}</td><td>{bar_html(it)}</td><td class="n">{it["done"]:,}/{it["cells"]:,}{extra}</td></tr>')
            out.append("</table>")
        log = p.get("log", [])[-10:]
        if log:
            out.append("<p><b>Recent steps</b></p><ul>" + "".join(f"<li>{escape(e['date'])}: {escape(e['text'])}</li>" for e in reversed(log)) + "</ul>")
    out.append("</body></html>")
    return "\n".join(out) + "\n"


def history_page(parts, hist):
    W, H, pad = 900, 260, 36
    n = len(hist)
    names = {str(p["part"]): f'{p["part"]} {p["name"]}' for p in parts}
    colours = ["#58a6ff", "#3fb950", "#d29922", "#db61a2", "#a371f7"]

    def xy(i, v):
        return pad + (W - 2 * pad) * (i / (n - 1) if n > 1 else 0.5), H - pad - (H - 2 * pad) * v / 100

    lines = [f'<line x1="{pad}" y1="{H - pad}" x2="{W - pad}" y2="{H - pad}" stroke="#30363d"/>']
    for v in (0, 25, 50, 75, 100):
        _, y = xy(0, v)
        lines.append(f'<text x="4" y="{y + 4:.0f}" fill="#8b949e" font-size="11" font-family="sans-serif">{v}%</text>')
    series = [("overall", "Whole project", "#ffffff")] + [(k, names[k], colours[i % 5]) for i, k in enumerate(names)]
    for key, name, colour in series:
        vals = [h["overall"] if key == "overall" else h["parts"].get(key, 0) for h in hist]
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (xy(i, v) for i, v in enumerate(vals)))
        lines.append(f'<polyline points="{pts}" fill="none" stroke="{colour}" stroke-width="{2.5 if key == "overall" else 1.5}"/>')
        lines += [f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.5" fill="{colour}"/>' for x, y in (xy(i, v) for i, v in enumerate(vals))]
    legend = " ".join(f'<span style="color:{c}">■</span> {escape(nm)}' for _, nm, c in series)
    rows = "".join(f'<tr><td>{h["date"]}</td><td class="n">{h["overall"]}%</td><td class="n">{h["tests"]}%</td>'
                   + "".join(f'<td class="n">{h["parts"].get(k, 0)}%</td>' for k in names) + "</tr>" for h in reversed(hist))
    head = "".join(f"<th class='n'>{escape(names[k])}</th>" for k in names)
    return "\n".join([PAGE_HEAD.format(title="STEM Racing car: progress history"),
                      "<h1>Progress history</h1>", '<p><a href="progress.html">Back to progress</a></p>',
                      f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}">{"".join(lines)}</svg>', f"<p>{legend}</p>",
                      f"<table><tr><th>Date</th><th class='n'>Whole project</th><th class='n'>Tests</th>{head}</tr>{rows}</table>",
                      "</body></html>"]) + "\n"


def main():
    parts = load_parts()
    overall, tests = tally(items(parts)), tally(items(parts, tests=True))
    signed = sum(1 for p in parts if p.get("status") == "done")
    updated = max(p.get("updated", "") for p in parts)
    svg = progress_svg(parts)
    write(BOARD / "progress.svg", svg)
    tl_text = timeline_svg(parts)
    write(BOARD / "timeline.svg", tl_text)
    badges = {
        "badge-overall.svg": badge("overall", f"{overall['percent']}%", scale_colour(overall["percent"])),
        "badge-tests.svg": badge("tests passed", f"{tests['done']:,}/{tests['total']:,}", scale_colour(tests["percent"])),
        "badge-parts.svg": badge("parts signed off", f"{signed}/{len(parts)}", "#007ec6"),
        "badge-updated.svg": badge("updated", updated, "#007ec6"),
    }
    for name, text in badges.items():
        write(BOARD / name, text)
        write(SITE / name, text)
    for old in ("header.svg", "overview.svg", *(f"part{p['part']}.svg" for p in parts)):
        (BOARD / old).unlink(missing_ok=True)
    hist = update_history(parts)
    write(ROOT / "README.md", readme(parts, overall, tests, signed))
    write(SITE / "progress.svg", svg)
    write(SITE / "progress.html", progress_page(parts, svg, list(badges), tl_text))
    write(SITE / "history.html", history_page(parts, hist))
    write(SITE / "index.html", '<!doctype html><meta http-equiv="refresh" content="0; url=progress.html">'
                               '<a href="progress.html">Progress</a>\n')
    write(SITE / ".nojekyll", "")
    print(f"board drawn: {overall['percent']}% overall, {tests['done']}/{tests['total']} tests")


if __name__ == "__main__":
    main()
