#!/usr/bin/env python3
"""Fix Oman WordPress content, install SEO plugin, add English pages, rebuild sitemap.

Credentials from the environment (never committed):
  WP_USER
  WP_APP_PASSWORD
  WP_ADMIN_PASSWORD   (wp-admin login, used only to upload the plugin zip)
  WP_BASE             default https://rukn-eltatawer.com/om
"""

from __future__ import annotations

import argparse
import base64
import html as htmlmod
import http.cookiejar
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from oman_copy import (
    CITIES,
    SERVICES,
    english_home_html,
    unique_ar_section,
    unique_en_article,
    unique_intro_ar,
)

CTX = ssl.create_default_context()
DEFAULT_BASE = "https://rukn-eltatawer.com/om"
PLUGIN_DIR = ROOT / "plugins" / "rukn-oman-seo"


class WP:
    def __init__(self, base: str, user: str, app_password: str):
        self.base = base.rstrip("/")
        token = base64.b64encode(f"{user}:{app_password}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {token}",
            "User-Agent": "RuknOmanSEO/1.3",
            "Accept": "application/json",
        }

    def url(self, route: str, **query) -> str:
        q = {"rest_route": route}
        q.update({k: v for k, v in query.items() if v is not None})
        return self.base + "/index.php?" + urllib.parse.urlencode(q)

    def request(self, method: str, route: str, data=None, query=None):
        headers = dict(self.headers)
        body = None
        if data is not None:
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json; charset=utf-8"
        req = urllib.request.Request(
            self.url(route, **(query or {})),
            data=body,
            headers=headers,
            method=method,
        )
        try:
            with urllib.request.urlopen(req, context=CTX, timeout=180) as resp:
                raw = resp.read()
                return resp.status, json.loads(raw) if raw else {}, dict(resp.headers)
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", "replace")
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                parsed = {"message": raw[:800], "status": e.code}
            return e.code, parsed, dict(e.headers)

    def get(self, route: str, **query):
        return self.request("GET", route, query=query)

    def post(self, route: str, data=None, **query):
        return self.request("POST", route, data=data, query=query)

    def delete(self, route: str, **query):
        return self.request("DELETE", route, query=query)


class Admin:
    def __init__(self, base: str, user: str, password: str):
        self.base = base.rstrip("/")
        self.user = user
        self.password = password
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPSHandler(context=CTX),
            urllib.request.HTTPCookieProcessor(self.jar),
        )

    def open(self, url: str, data=None, headers=None, method=None):
        hdrs = {"User-Agent": "RuknOmanSEO/1.3"}
        if headers:
            hdrs.update(headers)
        req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
        try:
            with self.opener.open(req, timeout=180) as resp:
                return resp.status, resp.read(), dict(resp.headers), resp.geturl()
        except urllib.error.HTTPError as e:
            return e.code, e.read(), dict(e.headers), getattr(e, "url", url)

    def login(self) -> None:
        login = self.base + "/wp-login.php"
        self.open(login)
        payload = urllib.parse.urlencode(
            {
                "log": self.user,
                "pwd": self.password,
                "wp-submit": "Log In",
                "redirect_to": self.base + "/wp-admin/",
                "testcookie": "1",
            }
        ).encode()
        code, body, _hdrs, final = self.open(
            login,
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        text = body.decode("utf-8", "replace")
        if "wp-admin" not in final or "login_error" in text:
            raise SystemExit(f"wp-admin login failed status={code} url={final} snippet={text[200:500]}")
        print("wp-admin login ok", final)

    def get_nonce(self, html: str, name: str = "_wpnonce") -> str:
        m = re.search(rf'name=["\']{name}["\'][^>]*value=["\']([^"\']+)["\']', html)
        if not m:
            m = re.search(rf'value=["\']([^"\']+)["\'][^>]*name=["\']{name}["\']', html)
        if not m:
            raise RuntimeError(f"nonce {name} not found")
        return m.group(1)


def split_slug(slug: str) -> tuple[str, str] | None:
    for city in sorted(CITIES, key=len, reverse=True):
        suffix = "-" + city
        if slug.endswith(suffix):
            svc = slug[: -len(suffix)]
            if svc in SERVICES:
                return svc, city
    return None


def strip_uae(text: str) -> str:
    replacements = [
        ("اختر الإمارة", "اختر المدينة"),
        ("خريطة الإمارات", "خريطة مدن عُمان"),
        ("الإمارات العربية المتحدة", "سلطنة عُمان"),
        ("دولة الإمارات", "سلطنة عُمان"),
        ("درهم إماراتي", "ريال عُماني"),
        ("الدرهم الإماراتي", "الريال العُماني"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    text = re.sub(r"\{PHONE_RUKN_OMAN\}", os.environ.get("WP_PHONE", "+971586634710"), text)
    text = re.sub(r"\{WHATSAPP_RUKN_OMAN\}", os.environ.get("WP_WHATSAPP", "971586634710"), text)
    return text


def inject_local(content: str, service: str, city: str) -> str:
    content = strip_uae(content)
    content = re.sub(
        r"<!--rukn-local-start-->.*?<!--rukn-local-end-->",
        "",
        content,
        flags=re.S,
    )
    content = re.sub(r"<h1(\b[^>]*)>", r"<h2\1>", content, count=1, flags=re.I)
    content = re.sub(r"</h1>", "</h2>", content, count=1, flags=re.I)
    intro = unique_intro_ar(service, city)
    content, n = re.subn(r"<p>.*?</p>", intro, content, count=1, flags=re.S)
    if n == 0:
        content = intro + content
    section = unique_ar_section(service, city)
    idx = content.rfind("</section>")
    if idx != -1:
        content = content[:idx] + section + content[idx:]
    else:
        content += section
    return content


def build_plugin_zip(dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        dest.unlink()
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in PLUGIN_DIR.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(PLUGIN_DIR.parent))
    print("plugin zip", dest, dest.stat().st_size)
    return dest


def encode_multipart(fields: dict[str, str], files: dict[str, tuple[str, bytes, str]]) -> tuple[bytes, str]:
    boundary = "----RuknOmanBoundary7MA4YWxkTrZu0gW"
    buf = bytearray()
    for name, value in fields.items():
        buf.extend(f"--{boundary}\r\n".encode())
        buf.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        buf.extend(value.encode() + b"\r\n")
    for name, (filename, blob, ctype) in files.items():
        buf.extend(f"--{boundary}\r\n".encode())
        buf.extend(
            f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'.encode()
        )
        buf.extend(f"Content-Type: {ctype}\r\n\r\n".encode())
        buf.extend(blob)
        buf.extend(b"\r\n")
    buf.extend(f"--{boundary}--\r\n".encode())
    return bytes(buf), f"multipart/form-data; boundary={boundary}"


def upload_plugin(admin: Admin, zip_path: Path) -> None:
    url = admin.base + "/wp-admin/plugin-install.php?tab=upload"
    code, body, _, _ = admin.open(url)
    html = body.decode("utf-8", "replace")
    if code != 200:
        raise SystemExit(f"plugin-install page {code}")
    nonce = admin.get_nonce(html)
    fields = {
        "_wpnonce": nonce,
        "_wp_http_referer": "/om/wp-admin/plugin-install.php?tab=upload",
        "install-plugin-submit": "Install Now",
    }
    if 'name="overwrite"' in html or "overwrite" in html:
        fields["overwrite"] = "update-plugin"
    payload, ctype = encode_multipart(
        fields,
        {"pluginzip": (zip_path.name, zip_path.read_bytes(), "application/zip")},
    )
    post_url = admin.base + "/wp-admin/update.php?action=upload-plugin"
    code, body, _, final = admin.open(
        post_url,
        data=payload,
        headers={"Content-Type": ctype},
    )
    text = body.decode("utf-8", "replace")
    print("upload plugin", code, final, "activate" in text.lower(), "error" in text.lower())
    if "Destination folder already exists" in text or "المجلد الوجهة موجود" in text:
        print("plugin folder exists — will activate/update via REST")
    act = re.search(r'href="(plugin-install\.php\?action=activate[^"]+)"', text)
    if not act:
        act = re.search(r'href="(plugins\.php\?action=activate[^"]+)"', text)
    if act:
        href = htmlmod.unescape(act.group(1)).replace("&amp;", "&")
        if href.startswith("http"):
            act_url = href
        else:
            act_url = admin.base + "/wp-admin/" + href.lstrip("/")
        code2, body2, _, final2 = admin.open(act_url)
        print("activate link", code2, final2)


def list_all_posts(wp: WP, route: str) -> list[dict]:
    items = []
    page = 1
    while True:
        code, data, hdrs = wp.get(route, per_page=100, page=page, context="edit", status="publish")
        if code != 200 or not isinstance(data, list):
            if page == 1:
                print("list fail", route, code, data)
            break
        items.extend(data)
        total_pages = int(hdrs.get("X-WP-TotalPages") or hdrs.get("x-wp-totalpages") or 1)
        if page >= total_pages:
            break
        page += 1
    return items


def existing_by_slug(wp: WP, route: str, slug: str) -> dict | None:
    code, data, _ = wp.get(route, slug=slug, status="any", per_page=20, context="edit")
    if code == 200 and isinstance(data, list):
        for item in data:
            if item.get("slug") == slug:
                return item
    return None


def service_html(slug: str) -> str:
    # Reuse importer-style copy with stronger Oman framing.
    names = {
        "water-leak-detection": ("كشف تسربات المياه", "تحديد مصدر التسرب بأجهزة حرارية قبل أي تكسير، مناسب لخزانات الأسطح وأنابيب الفلل في مناخ عُمان."),
        "roof-insulation": ("عزل الأسطح", "عزل حراري ومائي لأسطح تتعرض لشمس السلطنة صيفاً ورطوبة ساحلية في مسقط وصلالة."),
        "thermal-waterproof-insulation": ("العزل المائي والحراري", "حلول عزل للمباني والخزانات بالريال العُماني بعد معاينة سماكة السقف ونوع الخرسانة."),
        "general-maintenance": ("الصيانة العامة", "فريق واحد للأعطال اليومية في البيوت العُمانية دون جدولة منفصلة لكل حرفة."),
        "building-maintenance": ("صيانة المباني", "عقود صيانة للمجمعات والمباني الحكومية والتجارية في مدن السلطنة."),
        "plumbing": ("أعمال السباكة", "إصلاح شبكات المياه والصرف مع مراعاة ضغط الخزان الأرضي والعلوي الشائع في عُمان."),
        "sewer-clearing": ("تسليك المجاري", "تسليك بالضغط للمنازل والفلل، بما فيها الخطوط المتأثرة برمال الأودية."),
        "electrical-works": ("أعمال الكهرباء", "فحص لوحات وأفياش بما يناسب أحمال التكييف في الصيف العُماني."),
        "ac-install-maintenance": ("تركيب وصيانة التكييف", "تنظيف وصيانة الوحدات التي تعمل ساعات طويلة في حرارة مسقط والداخلية."),
        "cleaning-sterilization": ("التنظيف والتعقيم", "نظافة عميقة للغبار العُماني والرطوبة الساحلية بمواد تُوضَّح قبل التنفيذ."),
        "pest-control": ("مكافحة الحشرات", "معالجة آمنة للصراصير والنمل والقوارض مع متابعة تناسب المناخ الحار."),
        "landscaping": ("تنسيق الحدائق", "حدائق وأفنية تتحمل ملوحة بعض المياه وحرارة الظاهرة والباطنة."),
        "swimming-pools": ("إنشاء وصيانة المسابح", "صيانة مسابح الفلل في مسقط وصلالة مع معايرة الكيماويات حسب الغبار والأملاح."),
        "painting": ("الصبغ والدهانات", "دهانات داخلية وخارجية تتحمل الشمس والغبار دون وعود عامة خارج المعاينة."),
        "gypsum-board": ("تركيب الجبس بورد", "أسقف وقواطع تناسب التكييف المركزي والرطوبة الساحلية."),
        "interior-design": ("تصميم وتنفيذ الديكورات", "تشطيب مجالس وغرف بمعايير الضيافة العُمانية بعد مخطط واضح."),
    }
    title, lead = names.get(slug, (slug, "خدمة ميدانية في سلطنة عُمان."))
    return (
        f"<p>{lead} ركن التطور عُمان يعاين الموقع ثم يصدر عرض سعر مكتوب بالريال العُماني. "
        "التغطية: مسقط، صلالة، نزوى، صحار، صور، البريمي، عبري والرستاق.</p>"
        f"<p>هذه صفحة خدمة عامة بالعربي. مقالات التنظيف التفصيلية لكل مدينة مرتبطة من الصفحة الرئيسية.</p>"
    )


def fix_posts(wp: WP) -> None:
    posts = list_all_posts(wp, "/wp/v2/posts")
    print("posts", len(posts))
    updated = skipped = failed = 0
    for i, post in enumerate(posts, 1):
        slug = post.get("slug") or ""
        parsed = split_slug(slug)
        if not parsed:
            skipped += 1
            continue
        service, city = parsed
        raw = post["content"].get("raw") if isinstance(post.get("content"), dict) else ""
        if not raw:
            skipped += 1
            continue
        content = inject_local(raw, service, city)
        en = unique_en_article(service, city, post["title"].get("raw") or post["title"].get("rendered") or "")
        cinfo = CITIES[city]
        sinfo = SERVICES[service]
        title_meta = f"{sinfo['title_ar']} في {cinfo['ar']} | ركن التطور عُمان"
        desc_meta = (
            f"{sinfo['title_ar']} في {cinfo['ar']} داخل {cinfo['gov_ar']}. "
            f"معاينة ميدانية وسعر بالريال العُماني. تغطية: {cinfo['areas_ar'][:70]}."
        )[:160]
        payload = {
            "content": content,
            "excerpt": desc_meta,
            "meta": {
                "rank_math_title": title_meta,
                "rank_math_description": desc_meta,
                "_rukn_lang": "ar",
                "_rukn_pair_slug": slug,
                "_rukn_en_title": en["title"],
                "_rukn_en_content": en["html"],
                "_rukn_en_excerpt": en["excerpt"],
                "_rukn_en_desc": en["desc"],
            },
        }
        code, data, _ = wp.post(f"/wp/v2/posts/{post['id']}", payload)
        if code in (200, 201):
            updated += 1
            if i % 20 == 0 or i == 1:
                print(f"[{i}/{len(posts)}] update {slug} {code}")
        else:
            failed += 1
            print(f"[{i}/{len(posts)}] FAIL {slug} {code} {data}")
        time.sleep(0.08)
    print(json.dumps({"updated": updated, "skipped": skipped, "failed": failed}, ensure_ascii=False))


def fix_services(wp: WP) -> None:
    items = list_all_posts(wp, "/wp/v2/services")
    print("services", len(items))
    for item in items:
        slug = item.get("slug") or ""
        payload = {
            "content": service_html(slug),
            "meta": {
                "rank_math_title": f"{item['title'].get('raw') or item['title'].get('rendered')} | ركن التطور عُمان",
                "rank_math_description": "خدمة ميدانية في سلطنة عُمان مع معاينة وعرض سعر بالريال العُماني في مسقط وصلالة وباقي المدن.",
                "_rukn_lang": "ar",
                "_rukn_pair_slug": slug,
            },
        }
        code, data, _ = wp.post(f"/wp/v2/services/{item['id']}", payload)
        print("service", slug, code)


def upsert_english_home(wp: WP) -> None:
    html = english_home_html()
    payload = {
        "title": "Rukn Eltatawer Oman | Cleaning and home services",
        "slug": "en-home",
        "status": "publish",
        "content": html,
        "excerpt": "Home services across Oman: cleaning, leak detection, insulation and maintenance. Written quotes in OMR.",
        "meta": {
            "rank_math_title": "Rukn Eltatawer Oman | Cleaning, leak detection and maintenance in Muscat and all cities",
            "rank_math_description": "English guide to Rukn Eltatawer in the Sultanate of Oman. Cleaning and home services in Muscat, Salalah, Nizwa, Sohar, Sur, Al Buraimi, Ibri and Rustaq.",
            "_rukn_lang": "en",
            "_rukn_pair_slug": "home",
        },
    }
    existing = existing_by_slug(wp, "/wp/v2/pages", "en-home")
    if existing:
        code, data, _ = wp.post(f"/wp/v2/pages/{existing['id']}", payload)
        print("en-home update", code, data.get("id"))
    else:
        code, data, _ = wp.post("/wp/v2/pages", payload)
        print("en-home create", code, data.get("id"))


def site_settings(wp: WP) -> None:
    code, data, _ = wp.post(
        "/wp/v2/settings",
        {
            "title": "ركن التطور عُمان",
            "description": "خدمات منزلية متكاملة في سلطنة عُمان: تنظيف، كشف تسربات، عزل، صيانة وتكييف في مسقط وصلالة وباقي المدن.",
            "timezone": "Asia/Muscat",
            "default_comment_status": "closed",
            "default_ping_status": "closed",
        },
    )
    print("settings", code, {k: data.get(k) for k in ("title", "description", "timezone")} if isinstance(data, dict) else data)
    code, me, _ = wp.get("/wp/v2/users/me", context="edit")
    if code == 200:
        uid = me["id"]
        code, data, _ = wp.post(
            f"/wp/v2/users/{uid}",
            {"name": "فريق ركن التطور", "first_name": "ركن التطور", "last_name": "عُمان", "nickname": "ركن التطور عُمان"},
        )
        print("user", code, data.get("name") if isinstance(data, dict) else data)


def deactivate_conflicting_plugins(wp: WP) -> None:
    for slug in (
        "polylang/polylang",
        "code-snippets/code-snippets",
        "insert-headers-and-footers/ihaf",
    ):
        code, data, _ = wp.post(f"/wp/v2/plugins/{slug}", {"status": "inactive"})
        print(slug, code, data.get("status") if isinstance(data, dict) else data)


def delete_sample(wp: WP) -> None:
    page = existing_by_slug(wp, "/wp/v2/pages", "sample-page")
    if page:
        code, data, _ = wp.delete(f"/wp/v2/pages/{page['id']}", force="true")
        print("deleted sample-page", code)


def activate_plugin_rest(wp: WP) -> None:
    code, data, _ = wp.post("/wp/v2/plugins/rukn-oman-seo/rukn-oman-seo", {"status": "active"})
    print("plugin rest activate", code, data.get("status") if isinstance(data, dict) else str(data)[:300])


def theme_seo(admin: Admin) -> None:
    url = admin.base + "/wp-admin/admin.php?page=yts-theme__seo"
    code, body, _, final = admin.open(url)
    html = body.decode("utf-8", "replace")
    print("theme seo page", code, final, "seo" in html.lower())
    nonce_m = re.search(r'name="_wpnonce" value="([^"]+)"', html)
    # Collect input names if present.
    fields = {}
    for m in re.finditer(r'<input([^>]+)>', html, re.I):
        tag = m.group(1)
        name_m = re.search(r'name="([^"]+)"', tag)
        val_m = re.search(r'value="([^"]*)"', tag)
        typ_m = re.search(r'type="([^"]+)"', tag)
        if not name_m:
            continue
        name = htmlmod.unescape(name_m.group(1))
        typ = (typ_m.group(1) if typ_m else "text").lower()
        if typ in {"checkbox", "radio"} and "checked" not in tag.lower():
            continue
        fields[name] = htmlmod.unescape(val_m.group(1)) if val_m else ""
    for m in re.finditer(r'<textarea[^>]*name="([^"]+)"[^>]*>(.*?)</textarea>', html, re.I | re.S):
        fields[htmlmod.unescape(m.group(1))] = re.sub(r"<[^>]+>", "", m.group(2))
    updates = {
        "seo__site_name": "ركن التطور عُمان",
        "home__title": "ركن التطور عُمان | تنظيف وصيانة وكشف تسربات في مسقط وصلالة وكل مدن السلطنة",
        "home__description": "شركة خدمات منزلية في سلطنة عُمان: تنظيف منازل، كشف تسربات، عزل، صيانة وتكييف. عرض سعر بالريال العُماني بعد المعاينة.",
        "default__title": "{title} | ركن التطور عُمان",
        "default__description": "خدمات منزلية في سلطنة عُمان مع فريق مقيم ومعاينة قبل التنفيذ.",
    }
    applied = 0
    for key, val in updates.items():
        matched = [n for n in fields if key in n or n.endswith(key)]
        if not matched:
            # try nested arrays like theme_seo[seo__site_name]
            matched = [n for n in fields if key.split("__")[-1] in n]
        for n in matched:
            fields[n] = val
            applied += 1
            print("theme field", n, "<=", val[:60])
    if nonce_m:
        fields["_wpnonce"] = nonce_m.group(1)
    # Always try common Kayan names even if not in GET (disabled fields skipped).
    for k, v in updates.items():
        fields.setdefault(k, v)
        fields.setdefault(f"theme_seo[{k}]", v)
        fields.setdefault(f"yts[{k}]", v)
    if applied == 0 and not fields:
        print("theme seo form empty — skipping POST")
        return
    fields.setdefault("action", "save")
    payload = urllib.parse.urlencode(fields, doseq=True).encode()
    code, body, _, final = admin.open(
        url,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    print("theme seo save", code, final, len(body or b""))


def flush_permalinks(admin: Admin) -> None:
    url = admin.base + "/wp-admin/options-permalink.php"
    code, body, _, _ = admin.open(url)
    html = body.decode("utf-8", "replace")
    try:
        nonce = admin.get_nonce(html)
    except RuntimeError:
        print("permalinks nonce missing")
        return
    payload = urllib.parse.urlencode(
        {
            "_wpnonce": nonce,
            "_wp_http_referer": "/om/wp-admin/options-permalink.php",
            "permalink_structure": "/%postname%/",
            "category_base": "",
            "tag_base": "",
            "submit": "Save Changes",
        }
    ).encode()
    code, body, _, final = admin.open(
        url,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    print("permalinks", code, final)


def rebuild(wp: WP) -> None:
    code, data, _ = wp.post("/rukn-seo/v1/rebuild", {})
    print("rebuild", code, data)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-upload", action="store_true")
    parser.add_argument("--skip-content", action="store_true")
    args = parser.parse_args()

    user = os.environ.get("WP_USER")
    app = os.environ.get("WP_APP_PASSWORD")
    admin_pw = os.environ.get("WP_ADMIN_PASSWORD") or os.environ.get("WP_PASSWORD")
    if not user or not app:
        raise SystemExit("Set WP_USER and WP_APP_PASSWORD")
    base = os.environ.get("WP_BASE", DEFAULT_BASE)
    wp = WP(base, user, app)
    code, me, _ = wp.get("/wp/v2/users/me", context="edit")
    if code != 200:
        raise SystemExit(f"auth failed {code}: {me}")
    print("authenticated", me.get("slug"), me.get("roles"))

    if not args.skip_upload:
        if not admin_pw:
            raise SystemExit("Set WP_ADMIN_PASSWORD to upload the plugin")
        zip_path = build_plugin_zip(ROOT / "plugins" / "rukn-oman-seo.zip")
        admin = Admin(base, user, admin_pw)
        admin.login()
        # Prefer overwrite upload; if plugin exists REST-activate afterwards.
        code, data, _ = wp.get("/wp/v2/plugins/rukn-oman-seo/rukn-oman-seo")
        if code == 200:
            wp.post("/wp/v2/plugins/rukn-oman-seo/rukn-oman-seo", {"status": "inactive"})
            del_code, del_data, _ = wp.delete("/wp/v2/plugins/rukn-oman-seo/rukn-oman-seo")
            print("removed previous plugin", del_code, str(del_data)[:160])
        upload_plugin(admin, zip_path)
        activate_plugin_rest(wp)
        flush_permalinks(admin)
        try:
            theme_seo(admin)
        except Exception as exc:
            print("theme seo error", exc)
        deactivate_conflicting_plugins(wp)
    else:
        activate_plugin_rest(wp)
        deactivate_conflicting_plugins(wp)

    site_settings(wp)
    delete_sample(wp)
    upsert_english_home(wp)
    if not args.skip_content:
        fix_services(wp)
        fix_posts(wp)
    rebuild(wp)


if __name__ == "__main__":
    main()
