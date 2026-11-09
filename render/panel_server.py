#!/usr/bin/env python3
"""The live panel's web server, for the team's Oracle machine.

    python3 render/panel_server.py --port 8080

GET /          the panel page (render/live_page.html), asking /api for data
GET /api       the data; ?fresh=1 pulls the board repo and reads GitHub again
GET /healthz   "ok"

The board repo is a git clone (this file lives in it), so config and progress changes
arrive with `git pull`; nothing is hard-coded here. A read-only GitHub token is read from
the file named in PANEL_TOKEN_FILE (default /etc/stem-panel/token) if it exists; without
one, GitHub allows only 60 calls an hour from this machine. Standard library only.
"""
import argparse
import json
import os
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "render"))
import live  # noqa: E402

TOKEN_FILE = Path(os.environ.get("PANEL_TOKEN_FILE", "/etc/stem-panel/token"))
_lock = threading.Lock()
_cache = {"at": 0.0, "body": b""}


def token():
    try:
        t = TOKEN_FILE.read_text().strip()
        return t or None
    except OSError:
        return None


def pull():
    subprocess.run(["git", "-C", str(ROOT), "pull", "-q", "--ff-only"], capture_output=True, timeout=30)


def data(fresh):
    min_gap = live.load_config(ROOT)["limits"]["min_seconds_between_live_fetches"]
    with _lock:
        age = time.time() - _cache["at"]
        if _cache["body"] and (age < min_gap or (not fresh and age < 300)):
            return _cache["body"]
        if fresh or not _cache["body"]:
            pull()
        body = json.dumps(live.build_data(token(), ROOT, source="live")).encode()
        _cache.update(at=time.time(), body=body)
        return body


class Handler(BaseHTTPRequestHandler):
    server_version = "stem-panel"

    def _send(self, code, body, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        path, _, query = self.path.partition("?")
        try:
            if path in ("/", "/index.html", "/live.html"):
                self._send(200, live.page_html("/api", ROOT).encode(), "text/html; charset=utf-8")
            elif path == "/api":
                self._send(200, data("fresh=1" in query), "application/json")
            elif path == "/healthz":
                self._send(200, b"ok", "text/plain")
            else:
                self._send(404, b"not found", "text/plain")
        except Exception as exc:  # noqa: BLE001 - never crash the server
            self._send(500, json.dumps({"error": str(exc)[:200]}).encode(), "application/json")

    def log_message(self, fmt, *args):
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8080)
    a = ap.parse_args()
    ThreadingHTTPServer(("0.0.0.0", a.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
