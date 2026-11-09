#!/usr/bin/env python3
"""Live panel: what every part is doing and what is running on the 8 accounts' machines.

Runs inside the render workflow (every 5 min). Reads public GitHub Actions data with the
workflow's own GITHUB_TOKEN (a separate budget from the agents' accounts), never more than
MAX_CALLS requests per run. Writes site/live.html and site/live.json. Standard library only.
"""
import datetime as dt
import json
import os
import statistics
import urllib.request
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
REPO = "stem-racing-car"
MAX_CALLS = 60                 # per run; 12 runs an hour -> at most ~720 calls/hour
ACCOUNTS = {                   # account -> (jobs at once, default part, shared?)
    "shawshanker18": (40, None, True), "mxnviir": (40, None, True),
    "blackwingftc-lang": (20, 2, False), "Jdiejei": (20, 1, False),
    "instagramshashank8-bot": (20, 3, False), "blackwingstem-wq": (20, 3, False),
    "blackwinglinkedin-crypto": (14, 4, False), "anasssssssss1": (5, 4, False),
}
PART_NAMES = {1: "Cutter", 2: "Stopwatch", 3: "Compass", 4: "Parts and referee", 5: "Loop"}
WORK = {"stress": "random-car test", "tests": "test suite", "noise": "timing noise study",
        "noise_long": "timing noise study", "noise_var": "timing noise study", "repeat": "repeat check",
        "solver": "search round", "adj_lab": "compass lab", "car_debug": "one-car check",
        "body_lab": "lab run", "capacity": "capacity test", "impact": "impact study",
        "impact_wheels": "impact study", "smooth": "smoothness check", "line_lab": "lab run",
        "pinch_lab": "lab run", "car_libs": "library check"}

calls = 0


def get(path):
    global calls
    if calls >= MAX_CALLS:
        return None
    calls += 1
    req = urllib.request.Request("https://api.github.com" + path, headers={
        "Accept": "application/vnd.github+json", "User-Agent": "stem-racing-progress-live",
        **({"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"} if os.environ.get("GITHUB_TOKEN") else {})})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode())
    except Exception:  # noqa: BLE001 - a missing account or a hiccup must not stop the board
        return None


def when(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None


def is_part_wf(wf_file):
    return len(wf_file) > 2 and wf_file[0] == "p" and wf_file[1].isdigit() and wf_file[2] == "_"


def part_of(account, wf_file, title):
    for n in range(1, 6):
        if wf_file.startswith(f"p{n}_") or title.lower().startswith(f"part {n}"):
            return n
    return ACCOUNTS[account][1]


def collect():
    now = dt.datetime.now(dt.timezone.utc)
    runs, typical, busy = [], {}, {}
    for acct in ACCOUNTS:
        found = []
        for status in ("in_progress", "queued"):
            d = get(f"/repos/{acct}/{REPO}/actions/runs?status={status}&per_page=30")
            found += (d or {}).get("workflow_runs", [])
        busy[acct] = 0
        if found:
            done = get(f"/repos/{acct}/{REPO}/actions/runs?status=success&per_page=40") or {}
            for r in done.get("workflow_runs", []):
                a, b = when(r.get("run_started_at")), when(r.get("updated_at"))
                if a and b:
                    typical.setdefault((acct, r["path"]), []).append((b - a).total_seconds())
        for r in found:
            wf_file = Path(r.get("path", "")).stem
            title = r.get("display_title") or r.get("name") or wf_file
            jobs = (get(f"/repos/{acct}/{REPO}/actions/runs/{r['id']}/jobs?per_page=100") or {}).get("jobs", [])
            total = len(jobs) or 1
            n_done = sum(1 for j in jobs if j["status"] == "completed")
            running = [j for j in jobs if j["status"] == "in_progress"]
            busy[acct] += len(running)
            typ = statistics.median(typical.get((acct, r["path"]), [0])) or None
            frac = n_done
            for j in running:
                el = (now - when(j["started_at"])).total_seconds() if j.get("started_at") else 0
                frac += min(el / typ, 0.99) if typ else 0.5
            started = when(r.get("run_started_at") or r.get("created_at"))
            runs.append({
                "account": acct, "part": part_of(acct, wf_file, title),
                "title": title if is_part_wf(wf_file) or title.lower().startswith("part ") else WORK.get(wf_file, "run"),
                "status": r["status"], "started": started.isoformat() if started else None,
                "jobs_total": len(jobs), "jobs_done": n_done, "jobs_running": len(running),
                "percent": round(100 * frac / total, 1) if jobs else 0.0,
                "typical_min": round(typ / 60, 1) if typ else None})
    return {"generated": now.isoformat(), "runs": runs, "busy": busy, "api_calls": calls}


GATES = {3: (["A"], ["B"]), 5: (["A", "C", "D"], [])}   # part -> (required unlocks, helpful ones)
OWNER = {"A": 1, "B": 2, "C": 2, "D": 4}


def unlocks_status():
    u = {}
    for f in sorted((ROOT / "progress").glob("part*.json")):
        p = json.loads(f.read_text(encoding="utf-8"))
        for k, v in (p.get("unlocks") or {}).items():
            u[k] = {"label": v.get("label", k), "done": bool(v.get("done")), "date": v.get("date", ""), "part": p["part"]}
    gates = []
    for part, (need, nice) in GATES.items():
        missing = [k for k in need if not u.get(k, {}).get("done")]
        gates.append({"part": part, "ready": not missing, "missing": missing,
                      "helpful_missing": [k for k in nice if not u.get(k, {}).get("done")]})
    return u, gates


def parts_status():
    out = []
    for f in sorted((ROOT / "progress").glob("part*.json")):
        p = json.loads(f.read_text(encoding="utf-8"))
        ts = p.get("tasks", [])
        doing = [t["title"] for t in ts if t.get("status") == "doing"]
        out.append({"part": p["part"], "name": p["name"], "status": p.get("status"), "now": p.get("now", ""),
                    "updated": p.get("updated", ""), "doing": doing,
                    "done": sum(1 for t in ts if t.get("status") == "done"), "total": len(ts),
                    "blocked": [t["title"] for t in ts if t.get("status") == "blocked"],
                    "failed": [t["title"] for t in ts if t.get("status") == "failed"],
                    "tasks": [{"title": t["title"], "status": t.get("status", "todo")} for t in ts],
                    "last_log": (p.get("log") or [{}])[-1].get("text", "")})
    return out


CSS = """
:root{--bg:#0b0b0b;--panel:#121212;--line:#262626;--text:#ededed;--mute:#8a8a8a;--dim:#5a5a5a;--hi:#ffffff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);
font:14px/1.5 ui-sans-serif,-apple-system,"Segoe UI",Inter,Helvetica,Arial,sans-serif}
main{max-width:1080px;margin:0 auto;padding:28px 18px 60px}
header{display:flex;justify-content:space-between;align-items:baseline;border-bottom:1px solid var(--line);padding-bottom:14px}
h1{font-size:18px;font-weight:600;letter-spacing:.02em;margin:0}h2{font-size:12px;font-weight:600;letter-spacing:.14em;
text-transform:uppercase;color:var(--mute);margin:34px 0 12px}
.meta{color:var(--mute);font-size:12px}.num{font-variant-numeric:tabular-nums;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.grid{display:grid;gap:10px}.card{background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:14px 16px}
.row{display:grid;grid-template-columns:170px 1fr 120px;gap:14px;align-items:center}
.pname{font-weight:600}.pstate{color:var(--mute);font-size:12px}
.steps{display:flex;gap:3px;margin-top:8px}.steps i{flex:1;height:6px;border-radius:2px;background:#2a2a2a}
.steps i.done{background:#e6e6e6}.steps i.doing{background:#8f8f8f}.steps i.failed{background:#ffffff;outline:1px dashed #000}
.steps i.blocked{background:repeating-linear-gradient(45deg,#555 0 3px,#2a2a2a 3px 6px)}
.now{color:var(--text)}.sub{color:var(--mute);font-size:12px;margin-top:4px}
table{width:100%;border-collapse:collapse}th{color:var(--dim);font-weight:500;text-align:left;font-size:11px;letter-spacing:.08em;
text-transform:uppercase;padding:6px 8px;border-bottom:1px solid var(--line)}td{padding:9px 8px;border-bottom:1px solid #1a1a1a;vertical-align:middle}
.bar{height:4px;background:#262626;border-radius:2px;overflow:hidden;min-width:90px}.bar b{display:block;height:100%;background:#e6e6e6}
.empty{color:var(--dim);padding:14px 0}.acc{display:grid;grid-template-columns:200px 1fr 70px;gap:12px;align-items:center;padding:6px 0}
footer{margin-top:40px;color:var(--dim);font-size:12px}a{color:var(--text)}
.gate{display:grid;grid-template-columns:150px 120px 1fr;gap:14px;align-items:center;padding:8px 0;border-bottom:1px solid #1a1a1a}
.gate:last-child{border-bottom:0}.pill{display:inline-block;font-size:11px;letter-spacing:.12em;font-weight:700;padding:3px 8px;border-radius:3px;text-align:center}
.pill.go{background:#f2f2f2;color:#0b0b0b}.pill.wait{border:1px solid #3a3a3a;color:#8a8a8a}
.ul{display:grid;grid-template-columns:28px 1fr 110px;gap:10px;padding:5px 0;color:var(--mute)}.ul.ok{color:var(--text)}
@media(max-width:720px){.row{grid-template-columns:1fr}.acc{grid-template-columns:1fr 60px}.acc .bar{grid-column:1/-1}}
"""

JS = """
function ago(s){if(!s)return'';const m=Math.max(0,Math.round((Date.now()-Date.parse(s))/60000));
if(m<60)return m+' min ago';const h=Math.floor(m/60);return h+' h '+(m%60)+' min ago'}
for(const e of document.querySelectorAll('[data-t]'))e.textContent=ago(e.dataset.t);
setTimeout(()=>location.reload(),60000);
"""


def page(live, parts, unlocks=None, gates=None):
    P = []
    for p in parts:
        steps = "".join(f'<i class="{escape(t["status"])}" title="{escape(t["title"])}"></i>' for t in p["tasks"])
        state = {"active": "working", "waiting": "waiting to start", "done": "signed off"}.get(p["status"], p["status"] or "")
        extra = ""
        if p["blocked"]:
            extra += f'<div class="sub">Blocked: {escape(", ".join(p["blocked"]))}</div>'
        if p["failed"]:
            extra += f'<div class="sub">Being redone: {escape(", ".join(p["failed"]))}</div>'
        P.append(f'''<div class="card"><div class="row">
<div><div class="pname">Part {p["part"]} · {escape(p["name"])}</div><div class="pstate">{escape(state)}</div></div>
<div><div class="now">{escape(p["now"])}</div>
<div class="sub">{("Current step: " + escape("; ".join(p["doing"]))) if p["doing"] else ""}</div>{extra}
<div class="steps">{steps}</div></div>
<div class="num" style="text-align:right">{p["done"]}/{p["total"]} steps<div class="pstate">updated {escape(p["updated"])}</div></div>
</div></div>''')
    R = []
    for r in sorted(live["runs"], key=lambda r: (r["status"] != "in_progress", r["part"] or 9, r["account"])):
        part = f'Part {r["part"]}' if r["part"] else "shared"
        eta = ""
        if r["typical_min"] and r["status"] == "in_progress":
            eta = f'<div class="pstate">typical {r["typical_min"]:g} min</div>'
        R.append(f'''<tr><td>{part}</td><td>{escape(r["title"])}<div class="pstate">{escape(r["account"])}</div></td>
<td class="pstate">{"running" if r["status"] == "in_progress" else "queued"}</td>
<td class="num"><span data-t="{escape(r["started"] or "")}"></span>{eta}</td>
<td style="width:22%"><div class="bar"><b style="width:{r["percent"]}%"></b></div>
<div class="pstate num">{r["percent"]:g}% · {r["jobs_done"]}/{r["jobs_total"]} jobs done, {r["jobs_running"]} running</div></td></tr>''')
    A = []
    for acct, (cap, part, shared) in ACCOUNTS.items():
        n = live["busy"].get(acct, 0)
        who = "shared" if shared else f"Part {part}"
        A.append(f'''<div class="acc"><div>{escape(acct)}<div class="pstate">{who}</div></div>
<div class="bar"><b style="width:{min(100, 100 * n / cap):.1f}%"></b></div><div class="num" style="text-align:right">{n}/{cap}</div></div>''')
    G = []
    for g in gates or []:
        name = PART_NAMES[g["part"]]
        if g["ready"]:
            why = "Everything it needs is finished and tested. You can start it."
            if g["helpful_missing"]:
                why += " (Still coming, helpful but not required: " + ", ".join(
                    f'{k} from Part {OWNER[k]}' for k in g["helpful_missing"]) + ".)"
        else:
            why = "Waiting for: " + ", ".join(f'{k} ({unlocks.get(k, {}).get("label", k)}, from Part {OWNER[k]})' for k in g["missing"])
        G.append(f'<div class="gate"><div class="pname">Part {g["part"]} · {escape(name)}</div>'
                 f'<div><span class="pill {"go" if g["ready"] else "wait"}">{"READY TO START" if g["ready"] else "NOT YET"}</span></div>'
                 f'<div class="sub" style="margin:0">{escape(why)}</div></div>')
    U = []
    for k in sorted((unlocks or {})):
        v = unlocks[k]
        U.append(f'<div class="ul {"ok" if v["done"] else ""}"><div class="num">{"[x]" if v["done"] else "[ ]"}</div>'
                 f'<div>{escape(k)} · {escape(v["label"])} <span style="color:var(--dim)">(Part {v["part"]})</span></div>'
                 f'<div class="num" style="text-align:right">{escape(v["date"]) if v["done"] else "not yet"}</div></div>')
    gates_html = (f'<h2>Ready to start?</h2><div class="card">{"".join(G)}</div>'
                  f'<div class="card" style="margin-top:10px">{"".join(U)}</div>') if G else ""
    total_busy = sum(live["busy"].values())
    runs_html = ("<table><tr><th>Part</th><th>What</th><th>State</th><th>Started</th><th>Progress</th></tr>"
                 + "".join(R) + "</table>") if R else '<div class="empty">Nothing is running right now.</div>'
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>STEM Racing · live</title><style>{CSS}</style></head><body><main>
<header><h1>STEM Racing · live</h1><div class="meta">refreshed <span data-t="{live["generated"]}"></span> · page reloads every minute · data every ~5 min</div></header>
{gates_html}
<h2>Parts</h2><div class="grid">{"".join(P)}</div>
<h2>Running on GitHub <span class="num" style="color:var(--dim)">· {total_busy} machines busy</span></h2>{runs_html}
<h2>Machines in use per account</h2><div class="card">{"".join(A)}</div>
<footer>Progress only, no code or design data. <a href="progress.html">Full progress</a> · <a href="history.html">History</a> ·
<a href="https://github.com/shawshanker18/stem-racing-progress">Repository</a> · {live["api_calls"]} GitHub calls this refresh</footer>
</main><script>{JS}</script></body></html>
'''


def main():
    live = collect()
    parts = parts_status()
    unlocks, gates = unlocks_status()
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "live.json").write_text(json.dumps({"live": live, "parts": parts, "unlocks": unlocks, "gates": gates}, indent=1), encoding="utf-8")
    (SITE / "live.html").write_text(page(live, parts, unlocks, gates), encoding="utf-8")
    print(f"live page: {len(live['runs'])} runs, {sum(live['busy'].values())} machines busy, {live['api_calls']} API calls")


if __name__ == "__main__":
    main()
