#!/usr/bin/env python3
"""Live panel data: what every agent is doing and what runs on the accounts' machines.

Used two ways, with the same code:
  * GitHub Actions (render.yml, every 5-15 min): `python render/live.py` writes site/live.json
    and site/live.html (a snapshot; its Refresh button reloads that snapshot).
  * The Oracle server (render/panel_server.py): calls build_data() on demand, so Refresh
    gets live numbers.
Nothing about accounts, limits, parts or labels is in this file: it all comes from
config/panel.json and progress/part*.json. Standard library only.
"""
import datetime as dt
import json
import re
import os
import statistics
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
QUIET_HOURS = 3
AGENT_STATES = {"working": "WORKING", "waiting_on_compute": "WAITING ON COMPUTE",
                "needs_you": "NEEDS YOU", "blocked": "BLOCKED"}


def load_config(root=ROOT):
    return json.loads((root / "config" / "panel.json").read_text(encoding="utf-8"))


class GitHub:
    """Counts and caps API calls; reads with a token when one is given."""

    def __init__(self, token=None, max_calls=120):
        self.token, self.max_calls, self.calls, self.remaining = token, max_calls, 0, None

    def get(self, path):
        if self.calls >= self.max_calls or (self.remaining is not None and self.remaining < (50 if self.token else 2)):
            return None
        self.calls += 1
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "stem-racing-panel"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        try:
            with urllib.request.urlopen(urllib.request.Request("https://api.github.com" + path, headers=headers), timeout=20) as r:
                rem = r.headers.get("X-RateLimit-Remaining")
                self.remaining = int(rem) if rem is not None else self.remaining
                return json.loads(r.read().decode())
        except Exception:  # noqa: BLE001 - one bad account must not stop the panel
            return None


_FILEISH = re.compile(r"\s*\(?[\w./-]*\.(py|json|ya?ml|stl|npy|npz|csv|md|sh|txt)\)?", re.I)


def plain_title(s):
    """Run titles are shown publicly: drop anything that looks like a file name."""
    return re.sub(r"\s{2,}", " ", _FILEISH.sub("", s)).strip(" -:") or "run"


def when(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None


def _part_from(wf_file, title, default):
    for n in range(1, 10):
        if wf_file.startswith(f"p{n}_") or title.lower().startswith(f"part {n}"):
            return n
    return default


def collect_runs(cfg, gh):
    now = dt.datetime.now(dt.timezone.utc)
    runs, accounts = [], []
    for acc in cfg["accounts"]:
        name, repo = acc["name"], cfg["repo"]
        found = []
        for status in ("in_progress", "queued"):
            found += (gh.get(f"/repos/{name}/{repo}/actions/runs?status={status}&per_page=30") or {}).get("workflow_runs", [])
        typical = {}
        if found:
            for r in (gh.get(f"/repos/{name}/{repo}/actions/runs?status=success&per_page=40") or {}).get("workflow_runs", []):
                a, b = when(r.get("run_started_at")), when(r.get("updated_at"))
                if a and b:
                    typical.setdefault(r["path"], []).append((b - a).total_seconds())
        running_jobs = queued_jobs = 0
        for r in found:
            wf_file = Path(r.get("path", "")).stem
            title = r.get("display_title") or r.get("name") or wf_file
            plain = plain_title(title) if (wf_file[:1] == "p" and wf_file[1:2].isdigit()) or title.lower().startswith("part ") \
                else cfg["work_labels"].get(wf_file, "run")
            jobs = (gh.get(f"/repos/{name}/{repo}/actions/runs/{r['id']}/jobs?per_page=100") or {}).get("jobs", [])
            n_done = sum(1 for j in jobs if j["status"] == "completed")
            running = [j for j in jobs if j["status"] == "in_progress"]
            queued = [j for j in jobs if j["status"] in ("queued", "waiting", "pending")]
            running_jobs += len(running)
            queued_jobs += len(queued) if jobs else (1 if r["status"] == "queued" else 0)
            typ = statistics.median(typical[r["path"]]) if typical.get(r["path"]) else None
            frac = float(n_done)
            for j in running:
                el = (now - when(j["started_at"])).total_seconds() if j.get("started_at") else 0.0
                frac += min(el / typ, 0.99) if typ else 0.5
            started = when(r.get("run_started_at") or r.get("created_at"))
            runs.append({"account": name, "part": _part_from(wf_file, title, acc.get("part")), "title": plain,
                         "status": r["status"], "started": started.isoformat() if started else None,
                         "jobs_total": len(jobs), "jobs_done": n_done, "jobs_running": len(running),
                         "jobs_queued": len(queued),
                         "percent": round(100 * frac / len(jobs), 1) if jobs else 0.0,
                         "typical_min": round(typ / 60, 1) if typ else None})
        accounts.append({"name": name, "cap": acc["cap"], "part": acc.get("part"), "note": acc.get("note", ""),
                         "running": running_jobs, "queued": queued_jobs})
    return runs, accounts


def _last_update(root, part):
    """Last time the part's board file changed, from git history (no API call)."""
    try:
        out = subprocess.run(["git", "-C", str(root), "log", "-1", "--format=%cI", "--", f"progress/part{part}.json"],
                             capture_output=True, text=True, timeout=10).stdout.strip()
        return out or None
    except Exception:  # noqa: BLE001
        return None


def parts_and_agents(cfg, runs, root=ROOT):
    now = dt.datetime.now(dt.timezone.utc)
    parts, unlocks = [], {}
    for n in cfg["parts"]:
        f = root / "progress" / f"part{n}.json"
        if not f.exists():
            continue
        p = json.loads(f.read_text(encoding="utf-8"))
        ts = p.get("tasks", [])
        for k, v in (p.get("unlocks") or {}).items():
            unlocks[k] = {"label": v.get("label", k), "done": bool(v.get("done")), "date": v.get("date", ""), "part": n}
        mine = [r for r in runs if r["part"] == n]
        running = sum(r["jobs_running"] for r in mine)
        queued = sum(r["jobs_queued"] for r in mine) + sum(1 for r in mine if r["status"] == "queued" and not r["jobs_total"])
        last = _last_update(root, n)
        age_h = (now - when(last)).total_seconds() / 3600 if last else None
        blocked = [t["title"] for t in ts if t.get("status") == "blocked"]
        needs = (p.get("needs_you") or "").strip()
        said = AGENT_STATES.get((p.get("agent_state") or "").strip().lower())   # what the agent reports
        note = (p.get("agent_note") or "").strip()
        jobs_txt = f"{running} jobs running, {queued} queued on GitHub." if (running or queued) else ""
        if p.get("status") == "waiting":
            state, detail = "WAITING TO START", "Not started yet."
        elif p.get("status") == "done":
            state, detail = "SIGNED OFF", "Finished and signed off."
        elif needs or said == "NEEDS YOU":
            state, detail = "NEEDS YOU", needs or note or "Waiting for your answer."
        elif blocked or said == "BLOCKED":
            state, detail = "BLOCKED", note or "; ".join(blocked)
        elif said:
            state, detail = said, " ".join(x for x in (note, jobs_txt) if x) or ("Waiting for GitHub runs." if said == "WAITING ON COMPUTE" else "Working.")
        elif running or queued:
            state, detail = "WAITING ON COMPUTE", jobs_txt
        elif age_h is not None and age_h > QUIET_HOURS:
            state, detail = "QUIET", f"No update for {age_h:.0f} h."
        else:
            state, detail = "WORKING", "Working; nothing on GitHub right now."
        if age_h is not None and age_h > QUIET_HOURS and state in ("WORKING", "WAITING ON COMPUTE") and not (running or queued):
            state, detail = "QUIET", f"Says '{state.lower()}', but no update for {age_h:.0f} h."
        parts.append({"part": n, "name": p["name"], "status": p.get("status"), "now": p.get("now", ""),
                      "updated": p.get("updated", ""), "last_update": last, "state": state, "state_detail": detail,
                      "doing": [t["title"] for t in ts if t.get("status") == "doing"],
                      "done": sum(1 for t in ts if t.get("status") == "done"), "total": len(ts),
                      "tasks": [{"title": t["title"], "status": t.get("status", "todo")} for t in ts],
                      "jobs_running": running, "jobs_queued": queued})
    gates = []
    for g in cfg.get("gates", []):
        missing = [k for k in g["need"] if not unlocks.get(k, {}).get("done")]
        gates.append({"part": g["part"], "ready": not missing, "missing": missing,
                      "helpful_missing": [k for k in g.get("helpful", []) if not unlocks.get(k, {}).get("done")]})
    return parts, unlocks, gates


def build_data(token=None, root=ROOT, source="snapshot"):
    cfg = load_config(root)
    gh = GitHub(token, cfg["limits"]["max_calls_per_refresh"])
    runs, accounts = collect_runs(cfg, gh)
    parts, unlocks, gates = parts_and_agents(cfg, runs, root)
    return {"generated": dt.datetime.now(dt.timezone.utc).isoformat(), "source": source,
            "accounts": accounts, "runs": runs, "parts": parts, "unlocks": unlocks, "gates": gates,
            "api_calls": gh.calls, "rate_remaining": gh.remaining, "has_key": bool(token),
            "board": "https://github.com/shawshanker18/stem-racing-progress"}


def page_html(api_url, root=ROOT):
    return (root / "render" / "live_page.html").read_text(encoding="utf-8").replace("__API_URL__", api_url)


def main():
    cfg = load_config()
    data = build_data(os.environ.get("GITHUB_TOKEN"))
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "live.json").write_text(json.dumps(data, indent=1), encoding="utf-8")
    (SITE / "live.html").write_text(page_html(cfg.get("api_url") or "live.json"), encoding="utf-8")
    print(f"live page: {len(data['runs'])} runs, {sum(a['running'] for a in data['accounts'])} machines busy, "
          f"{data['api_calls']} API calls")


if __name__ == "__main__":
    main()
