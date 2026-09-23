#!/usr/bin/env python3
"""Write rukn-oman-seo plugin files to the live /om site via a Code Snippet."""

from __future__ import annotations

import base64
import gzip
import json
import os
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "rukn-oman-seo"
BASE = os.environ.get("WP_BASE", "https://rukn-eltatawer.com/om").rstrip("/")
CTX = ssl.create_default_context()
FILES = ("rukn-oman-seo.php", "frontend-fix.php", "kayan-blocks.php", "site-structure.php")


class WP:
    def __init__(self, base: str, user: str, app: str):
        token = base64.b64encode(f"{user}:{app}".encode()).decode()
        self.base = base.rstrip("/")
        self.headers = {
            "Authorization": f"Basic {token}",
            "User-Agent": "RuknHeaderFix/1.0",
            "Accept": "application/json",
        }

    def request(self, method: str, route: str, data=None, **query):
        q = {"rest_route": route, **{k: v for k, v in query.items() if v is not None}}
        url = self.base + "/index.php?" + urllib.parse.urlencode(q)
        headers = dict(self.headers)
        body = None
        if data is not None:
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json; charset=utf-8"
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, context=CTX, timeout=180) as resp:
                raw = resp.read().decode("utf-8", "replace")
                start = min([i for i in (raw.find("{"), raw.find("[")) if i >= 0], default=-1)
                parsed = json.JSONDecoder().raw_decode(raw[start:])[0] if start >= 0 else {}
                return resp.status, parsed
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", "replace")
            return e.code, {"message": raw[:400]}

    def get(self, route: str, **query):
        return self.request("GET", route, **query)

    def post(self, route: str, data=None, **query):
        return self.request("POST", route, data=data, **query)


def php_blob(path: Path) -> str:
    return base64.b64encode(gzip.compress(path.read_bytes())).decode("ascii")


def main() -> int:
    user = os.environ.get("WP_USER")
    app = os.environ.get("WP_APP_PASSWORD")
    if not user or not app:
        raise SystemExit("Set WP_USER and WP_APP_PASSWORD")
    wp = WP(BASE, user, app)
    parts = [f"'{name}' => '{php_blob(PLUGIN / name)}'" for name in FILES]
    php = """
$dir = WP_PLUGIN_DIR . '/rukn-oman-seo';
if (!is_dir($dir) && !wp_mkdir_p($dir)) { return; }
$files = [
""" + ",\n".join(parts) + """
];
foreach ($files as $name => $b64) {
    $raw = gzdecode(base64_decode($b64));
    if (is_string($raw) && $raw !== '') {
        file_put_contents($dir . '/' . $name, $raw);
    }
}
update_option('rukn_oman_plugin_files', '2.0.4');
if (function_exists('do_action')) {
    do_action('litespeed_purging_all');
    do_action('litespeed_purge_all');
}
"""
    payload = {
        "name": "Rukn Oman plugin writer",
        "desc": "Writes rukn-oman-seo plugin files (header 2.0.4).",
        "code": php.strip(),
        "scope": "global",
        "active": True,
        "priority": 1,
    }
    code, data = wp.get("/code-snippets/v1/snippets", per_page=50)
    found = None
    if code == 200 and isinstance(data, list):
        for item in data:
            if item.get("name") == "Rukn Oman plugin writer":
                found = item
                break
    if found:
        code, out = wp.request("PUT", f"/code-snippets/v1/snippets/{found['id']}", data=payload)
        print("update writer", code, flush=True)
        wp.request("PUT", f"/code-snippets/v1/snippets/{found['id']}", data={"active": True})
    else:
        code, out = wp.post("/code-snippets/v1/snippets", payload)
        print("create writer", code, flush=True)
    req = urllib.request.Request(
        BASE + "/",
        headers={"User-Agent": "RuknHeaderFix/1.0", "Cache-Control": "no-cache"},
    )
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=60) as resp:
            print("hit home", resp.status, flush=True)
    except Exception as e:
        print("hit home err", e, flush=True)
    print("deployed 2.0.4", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
