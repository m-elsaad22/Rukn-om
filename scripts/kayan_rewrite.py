#!/usr/bin/env python3
"""Rewrite Oman service posts with unique Kayan articles and fill theme blocks.

Credentials: WP_USER, WP_APP_PASSWORD, WP_BASE
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kayan_article_gen import ARTICLE_VER, build_article
from kayan_knowledge import CATALOG
from publish_schedule_oman import split_slug
from seo_fix_oman import WP, DEFAULT_BASE

ROOT = Path(__file__).resolve().parents[1]
SNIPPET_PHP = (ROOT / "plugins" / "rukn-oman-seo" / "kayan-blocks.php").read_text(encoding="utf-8")
PROGRESS = Path("/tmp/kayan-rewrite-progress.json")


def upsert_api_snippet(wp: WP) -> None:
    code, data, _ = wp.get("/code-snippets/v1/snippets", per_page=50)
    found = None
    if code == 200 and isinstance(data, list):
        for item in data:
            if item.get("name") == "Rukn Oman Kayan article API":
                found = item
                break
    payload = {
        "name": "Rukn Oman Kayan article API",
        "desc": "REST route to save unique article HTML and Kayan FAQ/features/steps/services/schema blocks",
        "code": SNIPPET_PHP.replace("<?php\n", "", 1),
        "scope": "global",
        "active": True,
        "priority": 8,
    }
    if found:
        code, data, _ = wp.request("PUT", f"/code-snippets/v1/snippets/{found['id']}", data=payload)
        print("kayan snippet update", code, data.get("active") if isinstance(data, dict) else data, flush=True)
    else:
        code, data, _ = wp.post("/code-snippets/v1/snippets", payload)
        print("kayan snippet create", code, data.get("id") if isinstance(data, dict) else data, flush=True)


def list_posts(wp: WP) -> list[dict]:
    items = []
    page = 1
    while True:
        code, data, hdrs = wp.get(
            "/wp/v2/posts",
            status="publish",
            per_page=100,
            page=page,
            context="edit",
            _fields="id,slug,title,meta",
        )
        if code != 200 or not isinstance(data, list) or not data:
            break
        items.extend(data)
        pages = int(hdrs.get("X-WP-TotalPages") or hdrs.get("x-wp-totalpages") or 1)
        if page >= pages:
            break
        page += 1
        time.sleep(0.05)
    return items


def load_progress() -> set[int]:
    if not PROGRESS.is_file():
        return set()
    try:
        return set(json.loads(PROGRESS.read_text()).get("done", []))
    except json.JSONDecodeError:
        return set()


def save_progress(done: set[int]) -> None:
    PROGRESS.write_text(json.dumps({"done": sorted(done), "ver": ARTICLE_VER}))


def save_article(wp: WP, post_id: int, art: dict) -> tuple[int, dict]:
    payload = {
        "content": art["content"],
        "excerpt": art["excerpt"],
        "tags": art["tags"],
        "meta": art["meta"],
    }
    return wp.post(f"/rukn/v1/article/{post_id}", payload)


def fallback_save(wp: WP, post_id: int, art: dict) -> tuple[int, dict]:
    payload = {
        "content": art["content"],
        "excerpt": art["excerpt"],
        "meta": {
            k: v
            for k, v in art["meta"].items()
            if isinstance(v, str) or k.startswith("_rukn") or k.startswith("rank_math")
        },
    }
    return wp.post(f"/wp/v2/posts/{post_id}", payload)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--only-slug", action="append", default=[])
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--delay", type=float, default=0.12)
    parser.add_argument("--skip-snippet", action="store_true")
    args = parser.parse_args()

    user = os.environ.get("WP_USER")
    app = os.environ.get("WP_APP_PASSWORD")
    if not user or not app:
        raise SystemExit("Set WP_USER and WP_APP_PASSWORD")
    wp = WP(os.environ.get("WP_BASE", DEFAULT_BASE), user, app)

    if not args.skip_snippet:
        upsert_api_snippet(wp)
        time.sleep(1.0)

    posts = list_posts(wp)
    print("listed", len(posts), flush=True)
    done = load_progress()
    updated = skipped = failed = 0
    only = set(args.only_slug)

    for i, post in enumerate(posts, 1):
        slug = post.get("slug") or ""
        if only and slug not in only:
            continue
        pid = int(post["id"])
        meta = post.get("meta") or {}
        if not args.force and (pid in done or meta.get("_rukn_article_ver") == ARTICLE_VER):
            skipped += 1
            done.add(pid)
            continue
        svc, city = split_slug(slug)
        title_obj = post.get("title") or {}
        title = title_obj.get("raw") or title_obj.get("rendered") or CATALOG.get(svc, slug)
        title = title.replace("&#8211;", "–")
        art = build_article(title, slug, svc, city)
        if art["words"] < 1000:
            print("THIN", slug, art["words"], flush=True)
        code, data, _ = save_article(wp, pid, art)
        if code not in (200, 201):
            code2, data2, _ = fallback_save(wp, pid, art)
            if code2 in (200, 201):
                code, data = code2, data2
                print("fallback wp/v2", slug, flush=True)
        if code in (200, 201):
            updated += 1
            done.add(pid)
            if updated % 10 == 0 or updated <= 3 or args.limit:
                print(
                    f"[{i}/{len(posts)}] ok {slug} words={art['words']} h2={len(art['h2'])}",
                    flush=True,
                )
        else:
            failed += 1
            print(f"FAIL {code} {slug} {str(data)[:240]}", flush=True)
        if updated % 25 == 0:
            save_progress(done)
        if args.limit and updated >= args.limit:
            break
        time.sleep(args.delay)

    save_progress(done)
    print(json.dumps({"updated": updated, "skipped": skipped, "failed": failed, "ver": ARTICLE_VER}, ensure_ascii=False))


if __name__ == "__main__":
    main()
