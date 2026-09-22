#!/usr/bin/env python3
"""Fill empty Kayan shortcode metaboxes (features/steps/prices/services/call) via LLM.

Default is dry-run. Nothing is written until you pass --apply.

Credentials from the environment or a repo-root .env (never commit .env):
  WP_USER, WP_APP_PASSWORD, WP_BASE
  OPENAI_API_KEY or GEMINI_API_KEY  (or --offline)
  WP_WHATSAPP=971586634710

Examples:
  python3 scripts/fill_kayan_fields.py --inspect-keys --post-id 1204
  python3 scripts/fill_kayan_fields.py --dry-run --offline --limit 3
  python3 scripts/fill_kayan_fields.py --apply --empty-only --limit 5 --provider openai
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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CTX = ssl.create_default_context()
DEFAULT_BASE = "https://rukn-eltatawer.com/om"
DEFAULT_MAP = Path(__file__).with_name("kayan_field_map.json")
DEFAULT_PROGRESS = ROOT / "fill-kayan-progress.json"
DEFAULT_LOG = ROOT / "fill-kayan-progress.jsonl"
WHATSAPP_DEFAULT = "971586634710"
CHECK_ICON = '<i class="fa-solid fa-check" style="color:#0056b3;"></i>'
TOOLS_ICON = '<i class="fa-solid fa-tools"></i>'
TABLE_HEAD_STYLE = "background:#0056b3;color:#fff;"

CITIES = {
    "muscat": "مسقط",
    "salalah": "صلالة",
    "nizwa": "نزوى",
    "sohar": "صحار",
    "sur": "صور",
    "al-buraimi": "البريمي",
    "ibri": "عبري",
    "rustaq": "الرستاق",
}
CITY_ALIASES = {
    "مسقط": "muscat",
    "صلالة": "salalah",
    "نزوى": "nizwa",
    "نزوه": "nizwa",
    "صحار": "sohar",
    "صور": "sur",
    "البريمي": "al-buraimi",
    "بريمي": "al-buraimi",
    "عبري": "ibri",
    "الرستاق": "rustaq",
    "رستاق": "rustaq",
}

LLM_INSTRUCTIONS = """أنت محرر تحويل في سلطنة عُمان لشركة خدمات منزلية اسمها «ركن التطور».
اكتب بالعربية الفصحى الواضحة، بلا إيموجي، وبسياق عُماني فقط (ريال عُماني، مناخ عُمان، المدينة المذكورة).
ممنوع ذكر الإمارات أو درهم أو دبي. ممنوع أرقام هاتف للاتصال. واتساب فقط: {whatsapp}.
العنوان يحدد الخدمة والمدينة.
لا تغيّر عنوان المقال ولا تقترح URL جديداً.
لا تخترع أسعاراً أو أرقاماً تجارية أو نسب خصم أو ضمانات. لا توجد قائمة أسعار مؤكدة.

أرجع JSON فقط بالمفاتيح التالية:
{{
  "service_ar": "اسم الخدمة دون كلمة شركة إن أمكن",
  "city_ar": "المدينة كما في العنوان",
  "features_title": "عنوان قسم المميزات ويشمل الخدمة والمدينة",
  "features_intro": "جملة أو جملتان",
  "features": [{{"title": "...", "content": "..."}}]  // بالضبط 4 عناصر فريدة
  "steps_title": "عنوان خطوات العمل",
  "steps_intro": "جملة",
  "steps": [{{"title": "...", "content": "..."}}]  // 3 أو 4 خطوات مهنية
  "prices_title": "عنوان يوضح أن التسعير بالريال العُماني بعد المعاينة",
  "prices_intro": "جملة صريحة: لا سعر ثابت في الصفحة، والقيمة تُكتب بعد المعاينة",
  "prices": [{{"title": "عامل يؤثر على التكلفة", "value": "يُحدد بعد المعاينة"}}]  // 4 صفوف. value دائماً يُحدد بعد المعاينة بلا أرقام
  "services_title": "خدمات مرتبطة في نفس المدينة",
  "services_intro": "جملة",
  "services": [{{"title": "...", "content": "..."}}]  // بالضبط 3 خدمات فرعية مرتبطة
  "call_title": "دعوة قوية للحجز في المدينة",
  "call_content": "CTA يذكر توفر الفريق بسرعة داخل المدينة، ويذكر واتساب {whatsapp} دون زر اتصال هاتفي"
}}
"""


def log(msg: str) -> None:
    print(msg, flush=True)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip().strip("'").strip('"')
        if key and key not in os.environ:
            os.environ[key] = val


def json_from_text(text: str) -> dict:
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    start = min([i for i in (text.find("{"),) if i >= 0], default=-1)
    if start < 0:
        raise ValueError("LLM did not return JSON")
    payload, _ = json.JSONDecoder().raw_decode(text[start:])
    if not isinstance(payload, dict):
        raise ValueError("LLM JSON is not an object")
    return payload


def strip_html(html: str) -> str:
    text = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", " ", html or "", flags=re.I | re.S)
    text = htmlmod.unescape(re.sub(r"<[^>]+>", " ", text))
    return re.sub(r"\s+", " ", text).strip()


def split_slug(slug: str) -> tuple[str, str]:
    slug = (slug or "").strip("/")
    for city in sorted(CITIES, key=len, reverse=True):
        suffix = "-" + city
        if slug.endswith(suffix):
            return slug[: -len(suffix)], city
    return slug, ""


def city_from_title(title: str) -> str:
    for ar, slug in sorted(CITY_ALIASES.items(), key=lambda kv: -len(kv[0])):
        if ar in (title or ""):
            return slug
    return ""


def service_label(title: str, city_ar: str) -> str:
    t = (title or "").strip()
    t = re.sub(r"^شركة\s+", "", t)
    if city_ar:
        t = t.replace(f" في {city_ar}", "").replace(f" {city_ar}", "")
    return t.strip(" -–—") or title


def sleep_delay(seconds: float) -> None:
    if seconds and seconds > 0:
        time.sleep(seconds)


class WP:
    def __init__(self, base: str, user: str, app_password: str):
        self.base = base.rstrip("/")
        token = base64.b64encode(f"{user}:{app_password}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {token}",
            "User-Agent": "RuknKayanFill/1.0",
            "Accept": "application/json",
        }

    def url(self, route: str, **query) -> str:
        q = {"rest_route": route}
        q.update({k: v for k, v in query.items() if v is not None})
        return self.base + "/index.php?" + urllib.parse.urlencode(q)

    def request(self, method: str, route: str, data=None, query=None, timeout: int = 180):
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
            with urllib.request.urlopen(req, context=CTX, timeout=timeout) as resp:
                raw = resp.read()
                text = raw.decode("utf-8", "replace") if raw else ""
                parsed: Any = {}
                if text:
                    start = min([i for i in (text.find("{"), text.find("[")) if i >= 0], default=-1)
                    if start >= 0:
                        parsed, _ = json.JSONDecoder().raw_decode(text[start:])
                    else:
                        parsed = {"message": text[:800]}
                return resp.status, parsed, dict(resp.headers)
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", "replace")
            try:
                start = min([i for i in (raw.find("{"), raw.find("[")) if i >= 0], default=-1)
                parsed = json.JSONDecoder().raw_decode(raw[start:])[0] if start >= 0 else {"message": raw[:800], "status": e.code}
            except json.JSONDecodeError:
                parsed = {"message": raw[:800], "status": e.code}
            return e.code, parsed, dict(e.headers)
        except (TimeoutError, OSError) as e:
            return 599, {"message": str(e)[:200]}, {}

    def get(self, route: str, **query):
        return self.request("GET", route, query=query)

    def post(self, route: str, data=None, **query):
        return self.request("POST", route, data=data, query=query)

    def put(self, route: str, data=None, **query):
        return self.request("PUT", route, data=data, query=query)


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

    def open(self, url: str, data=None, headers=None):
        hdrs = {"User-Agent": "RuknKayanFill/1.0"}
        if headers:
            hdrs.update(headers)
        req = urllib.request.Request(url, data=data, headers=hdrs)
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
            raise SystemExit(f"wp-admin login failed status={code} url={final}")
        log(f"wp-admin login ok {final}")

    def post_editor_html(self, post_id: int) -> str:
        url = f"{self.base}/wp-admin/post.php?post={post_id}&action=edit"
        _code, body, _h, _u = self.open(url)
        return body.decode("utf-8", "replace")


def fetch_public(url: str, timeout: int = 60) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "RuknKayanFill/1.0", "Accept": "text/html"})
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except (TimeoutError, OSError) as e:
        return 599, str(e)


def fetch_one(wp: WP, post_id: int) -> dict | None:
    code, data, _ = wp.get(
        f"/wp/v2/posts/{post_id}",
        context="edit",
        _fields="id,slug,link,title,content,status",
    )
    if code == 200 and isinstance(data, dict):
        return data
    log(f"fetch post {post_id} failed {code} {str(data)[:200]}")
    return None


def fetch_posts(wp: WP, delay: float, only_ids: list[int] | None = None) -> list[dict]:
    if only_ids:
        items = []
        for pid in only_ids:
            row = fetch_one(wp, pid)
            if row:
                items.append(row)
            sleep_delay(delay)
        return items
    items: list[dict] = []
    page = 1
    per_page = 20
    while True:
        code, data, hdrs = (0, None, {})
        last_err = ""
        for attempt in range(1, 6):
            code, data, hdrs = wp.get(
                "/wp/v2/posts",
                status="publish",
                per_page=per_page,
                page=page,
                context="view",
                _fields="id,slug,link,title",
            )
            if code == 200 and isinstance(data, list):
                break
            last_err = str(data)[:240]
            log(f"fetch page {page} attempt {attempt} code={code} {last_err}")
            if code == 400 and page > 1:
                return items
            sleep_delay(min(20, delay + 2 ** attempt))
        if code != 200 or not isinstance(data, list):
            raise SystemExit(f"fetch posts failed page={page} code={code} {last_err}")
        items.extend(data)
        total_pages = int(hdrs.get("X-WP-TotalPages") or hdrs.get("x-wp-totalpages") or page)
        log(f"fetched /wp/v2/posts page {page}/{total_pages} (+{len(data)}) total {len(items)}")
        if page >= total_pages or not data:
            break
        page += 1
        sleep_delay(max(delay, 0.25))
    return items


def classify_public_empty(posts: list[dict], workers: int = 8) -> dict[int, tuple[bool, str]]:
    from concurrent.futures import ThreadPoolExecutor, as_completed

    def check(post: dict) -> tuple[int, bool, str]:
        if not post.get("link"):
            return post["id"], True, "no-link"
        _st, html = fetch_public(post["link"], timeout=45)
        empty = public_is_empty(html)
        reason = "public-leftover-shortcodes" if empty else "public-expanded"
        return post["id"], empty, reason

    out: dict[int, tuple[bool, str]] = {}
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futs = [pool.submit(check, p) for p in posts]
        done = 0
        for fut in as_completed(futs):
            pid, empty, reason = fut.result()
            out[pid] = (empty, reason)
            done += 1
            if done % 50 == 0 or done == len(posts):
                log(f"classified public HTML {done}/{len(posts)}")
    return out


def unpack_post(item: dict) -> dict:
    title = item.get("title") or {}
    content = item.get("content") or {}
    title_txt = title.get("raw") or strip_html(title.get("rendered") or "")
    raw = content.get("raw") or content.get("rendered") or ""
    slug = item.get("slug") or ""
    service, city = split_slug(slug)
    if not city:
        city = city_from_title(title_txt)
    city_ar = CITIES.get(city, "")
    if not city_ar:
        for ar, slug_c in CITY_ALIASES.items():
            if ar in title_txt:
                city_ar = ar
                city = slug_c
                break
    return {
        "id": int(item["id"]),
        "slug": slug,
        "link": item.get("link") or "",
        "title": title_txt,
        "raw": raw,
        "service": service,
        "city": city,
        "city_ar": city_ar or "عُمان",
        "service_ar": service_label(title_txt, city_ar),
        "has_shortcodes": bool(re.search(r"\[post_(features|steps|prices|services|call)\]", raw)) or not raw,
    }


def editor_input_names(html: str) -> list[str]:
    names = re.findall(r'name="([^"]*post__(?:features|work_steps|price_list|services|call_section)[^"]*)"', html)
    extra = re.findall(r'name="(hide_(?:features__section|work_steps|price_list__section|services_section|call_section))"', html)
    seen = []
    for n in names + extra:
        if n not in seen:
            seen.append(n)
    return seen


def editor_value(html: str, name: str) -> str:
    pat_input = re.compile(
        r'<(?:input|textarea)\b[^>]*name="' + re.escape(name) + r'"[^>]*(?:value="([^"]*)")?',
        re.I,
    )
    m = pat_input.search(html)
    if not m:
        return ""
    tag = m.group(0)
    if tag.lower().startswith("<textarea"):
        m2 = re.search(
            r'<textarea\b[^>]*name="' + re.escape(name) + r'"[^>]*>(.*?)</textarea>',
            html,
            re.I | re.S,
        )
        return htmlmod.unescape(m2.group(1)).strip() if m2 else ""
    val = m.group(1) or ""
    vm = re.search(r'\bvalue="([^"]*)"', tag)
    if vm:
        val = vm.group(1)
    return htmlmod.unescape(val).strip()


def public_is_empty(html: str) -> bool:
    if not html:
        return True
    leftover = re.findall(r"\[post_(features|steps|prices|services|call)\]", html)
    return bool(leftover)


def features_html(features: list[dict]) -> str:
    items = []
    for row in features:
        title = htmlmod.escape(str(row.get("title") or "").strip())
        content = htmlmod.escape(str(row.get("content") or "").strip())
        items.append(f"<li>{CHECK_ICON} <strong>{title}</strong> — {content}</li>")
    return '<ul class="rukn-kayan-features">' + "".join(items) + "</ul>"


def steps_html(steps: list[dict]) -> str:
    items = []
    for i, row in enumerate(steps, 1):
        title = htmlmod.escape(str(row.get("title") or "").strip())
        content = htmlmod.escape(str(row.get("content") or "").strip())
        items.append(f"<li><strong>الخطوة {i}: {title}</strong> — {content}</li>")
    return '<ol class="rukn-kayan-steps">' + "".join(items) + "</ol>"


def prices_html(rows: list[dict]) -> str:
    body = []
    for row in rows:
        title = htmlmod.escape(str(row.get("title") or "").strip())
        value = htmlmod.escape(str(row.get("value") or "").strip())
        body.append(f'<tr><td style="padding:8px;border:1px solid #d9e2ec;">{title}</td>'
                    f'<td style="padding:8px;border:1px solid #d9e2ec;">{value}</td></tr>')
    return (
        '<div class="responsive-table"><table style="width:100%;border-collapse:collapse;">'
        "<thead><tr>"
        f'<th style="padding:10px;text-align:right;{TABLE_HEAD_STYLE}">البند</th>'
        f'<th style="padding:10px;text-align:right;{TABLE_HEAD_STYLE}">التقدير (ر.ع)</th>'
        "</tr></thead><tbody>"
        + "".join(body)
        + "</tbody></table></div>"
        '<p style="font-size:.9rem;">لا توجد أسعار ثابتة في هذه الصفحة. التكلفة بالريال العُماني تُكتب بعد المعاينة وليست عرضاً ملزماً مسبقاً.</p>'
    )


def services_html(rows: list[dict]) -> str:
    items = []
    for row in rows:
        title = htmlmod.escape(str(row.get("title") or "").strip())
        content = htmlmod.escape(str(row.get("content") or "").strip())
        items.append(f"<li>{TOOLS_ICON} <strong>{title}</strong> — {content}</li>")
    return '<ul class="rukn-kayan-services">' + "".join(items) + "</ul>"


def take_list(payload: dict, key: str, nmin: int, nmax: int) -> list[dict]:
    rows = payload.get(key) or []
    if not isinstance(rows, list):
        raise ValueError(f"{key} is not a list")
    clean = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        title = str(row.get("title") or "").strip()
        extra = str(row.get("content") or row.get("value") or "").strip()
        if not title:
            continue
        item = {"title": title}
        if "value" in row or key == "prices":
            item["value"] = str(row.get("value") or extra)
        else:
            item["content"] = extra
        clean.append(item)
    if len(clean) < nmin:
        raise ValueError(f"{key} needs at least {nmin} items, got {len(clean)}")
    return clean[:nmax]


def sanitize_price_value(value: str) -> str:
    text = (value or "").strip()
    if re.search(r"\d", text) and "معاينة" not in text:
        return "يُحدد بعد المعاينة"
    if re.search(r"\d+(?:\.\d+)?\s*(?:[–\-إلى]|ر\.?\s*ع)", text):
        return "يُحدد بعد المعاينة"
    return text or "يُحدد بعد المعاينة"


def validate_generated(payload: dict) -> dict:
    out = dict(payload)
    out["features"] = take_list(payload, "features", 4, 4)
    out["steps"] = take_list(payload, "steps", 3, 4)
    out["prices"] = take_list(payload, "prices", 3, 6)
    for row in out["prices"]:
        row["value"] = sanitize_price_value(row.get("value") or "")
    out["services"] = take_list(payload, "services", 3, 3)
    for key in (
        "features_title",
        "features_intro",
        "steps_title",
        "steps_intro",
        "prices_title",
        "prices_intro",
        "services_title",
        "services_intro",
        "call_title",
        "call_content",
    ):
        out[key] = str(payload.get(key) or "").strip()
        if not out[key]:
            raise ValueError(f"missing {key}")
    banned = re.compile(r"دبي|أبوظبي|ابوظبي|درهم|الإمارات|إمارة")
    blob = json.dumps(out, ensure_ascii=False)
    if banned.search(blob):
        raise ValueError("generated copy mentions UAE/AED")
    if re.search(r"[\U0001F300-\U0001FAFF]", blob):
        raise ValueError("generated copy contains emoji")
    return out


def offline_generate(post: dict, whatsapp: str) -> dict:
    city = post["city_ar"]
    svc = post["service_ar"]
    bands = [
        ("معاينة وتشخيص الحالة", "يُحدد بعد المعاينة"),
        (f"نطاق تنفيذ {svc}", "يُحدد بعد المعاينة"),
        ("خامات أو مساحة إضافية", "يُحدد بعد المعاينة"),
        ("زيارة عاجلة داخل المدينة", "يُحدد بعد المعاينة"),
    ]
    payload = {
        "service_ar": svc,
        "city_ar": city,
        "features_title": f"مميزات {svc} في {city}",
        "features_intro": f"فريق ميداني داخل {city} يربط التشخيص بالمناخ المحلي والتسعير بالريال العُماني.",
        "features": [
            {"title": "معاينة قبل التنفيذ", "content": f"لا نبدأ {svc} في {city} قبل تحديد النطاق على أرض الواقع."},
            {"title": "عرض مكتوب بالريال العُماني", "content": "البند والسعر يُذكران قبل العمل؛ أي إضافة تُوافق كتابياً."},
            {"title": "عدة تناسب مناخ عُمان", "content": "الحرارة والغبار والرطوبة تُؤخذ في اختيار المادة وطريقة التنفيذ."},
            {"title": "تواصل واتساب واضح", "content": f"صورة العطل أو وصف مختصر يكفي لترتيب زيارة داخل {city}."},
        ],
        "steps_title": f"خطوات {svc} في {city}",
        "steps_intro": "التسلسل إطار مهني؛ ترتيب البنود قد يتغير إذا تطلبت السلامة ذلك.",
        "steps": [
            {"title": "وصف الحالة وتحديد الموعد", "content": f"نستقبل التفاصيل عبر واتساب ونؤكد زيارة في {city}."},
            {"title": "فحص الموقع وتوثيق النطاق", "content": "نحدد المصدر والمساحة والخامة الظاهرة قبل أي إصلاح."},
            {"title": "تنفيذ المتفق عليه فقط", "content": "العمل يلتزم بالعرض. ما لم يُذكر يبقى خارج الفاتورة."},
            {"title": "مراجعة التسليم", "content": "ملخص ما أُنجز وما يحتاج زيارة لاحقة إن وُجد."},
        ],
        "prices_title": f"تسعير {svc} في {city} بعد المعاينة",
        "prices_intro": "لا نضع أسعاراً ثابتة هنا. القيمة بالريال العُماني تُكتب بعد فحص الموقع في المدينة.",
        "prices": [{"title": t, "value": v} for t, v in bands],
        "services_title": f"خدمات مرتبطة في {city}",
        "services_intro": "قد تكشف المعاينة حاجة مجاورة؛ كل بند يُسعَّر منفصلاً.",
        "services": [
            {"title": "فحص إضافي للنقطة المجاورة", "content": f"إذا ظهر عطل ملاصق أثناء {svc} نذكره قبل التنفيذ."},
            {"title": "صيانة وقائية بعد التسليم", "content": "تعليمات بسيطة تقلل عودة المشكلة في مناخ المدينة."},
            {"title": "إعادة زيارة عند الحاجة", "content": "خامة غير متوفرة أو بند جديد لا يُنفَّذ صامتاً."},
        ],
        "call_title": f"احجز {svc} في {city} اليوم",
        "call_content": (
            f"الفريق متاح بسرعة داخل {city}. أرسل وصفاً أو صورة عبر واتساب {whatsapp} "
            f"لنحدد موعد معاينة {svc} دون انتظار رقم اتصال هاتفي."
        ),
    }
    return validate_generated(payload)


def openai_generate(model: str, api_key: str, post: dict, whatsapp: str) -> dict:
    prompt = LLM_INSTRUCTIONS.format(whatsapp=whatsapp)
    user = (
        f"عنوان المقال: {post['title']}\n"
        f"slug: {post['slug']}\n"
        f"الخدمة المستخرجة: {post['service_ar']}\n"
        f"المدينة المستخرجة: {post['city_ar']}\n"
    )
    body = {
        "model": model,
        "temperature": 0.7,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user},
        ],
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "RuknKayanFill/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, context=CTX, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    text = data["choices"][0]["message"]["content"]
    return validate_generated(json_from_text(text))


def gemini_generate(model: str, api_key: str, post: dict, whatsapp: str) -> dict:
    prompt = LLM_INSTRUCTIONS.format(whatsapp=whatsapp)
    user = (
        f"{prompt}\n\nعنوان المقال: {post['title']}\nslug: {post['slug']}\n"
        f"الخدمة: {post['service_ar']}\nالمدينة: {post['city_ar']}\n"
    )
    qs = urllib.parse.urlencode({"key": api_key})
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?{qs}"
    body = {
        "contents": [{"parts": [{"text": user}]}],
        "generationConfig": {
            "temperature": 0.7,
            "responseMimeType": "application/json",
        },
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "RuknKayanFill/1.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, context=CTX, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    text = data["candidates"][0]["content"]["parts"][0]["text"]
    return validate_generated(json_from_text(text))


def generate_fields(provider: str, post: dict, args, whatsapp: str) -> dict:
    last_err: Exception | None = None
    for attempt in range(1, 4):
        try:
            if provider == "offline":
                return offline_generate(post, whatsapp)
            if provider == "openai":
                key = os.environ.get("OPENAI_API_KEY") or ""
                if not key:
                    raise SystemExit("OPENAI_API_KEY is missing")
                return openai_generate(args.openai_model, key, post, whatsapp)
            if provider == "gemini":
                key = os.environ.get("GEMINI_API_KEY") or ""
                if not key:
                    raise SystemExit("GEMINI_API_KEY is missing")
                return gemini_generate(args.gemini_model, key, post, whatsapp)
            raise SystemExit(f"unknown provider {provider}")
        except urllib.error.HTTPError as e:
            last_err = e
            raw = e.read().decode("utf-8", "replace")[:240]
            log(f"  LLM HTTP {e.code} attempt {attempt}: {raw}")
            if e.code in {429, 500, 502, 503}:
                sleep_delay(min(32, 2 ** attempt))
                continue
            raise
        except (ValueError, KeyError, json.JSONDecodeError) as e:
            last_err = e
            log(f"  LLM parse/validate attempt {attempt}: {e}")
            sleep_delay(1.0)
    raise RuntimeError(f"LLM failed after retries: {last_err}")


def pick_provider(args) -> str:
    if args.offline:
        return "offline"
    choice = (args.provider or os.environ.get("LLM_PROVIDER") or "auto").lower()
    if choice == "offline":
        return "offline"
    if choice == "auto":
        if os.environ.get("OPENAI_API_KEY"):
            return "openai"
        if os.environ.get("GEMINI_API_KEY"):
            return "gemini"
        raise SystemExit("Set OPENAI_API_KEY or GEMINI_API_KEY (do not use --offline for production fills).")
    if choice in {"openai", "gemini"}:
        env_name = "OPENAI_API_KEY" if choice == "openai" else "GEMINI_API_KEY"
        if not os.environ.get(env_name):
            raise SystemExit(f"{env_name} is missing")
    return choice


def build_kayan_meta(generated: dict, whatsapp: str) -> dict:
    features = generated["features"]
    steps = generated["steps"]
    prices = generated["prices"]
    services = generated["services"]
    feat_html = features_html(features)
    intro = generated["features_intro"]
    return {
        "post__features__data": {
            "features__title": generated["features_title"],
            "features__content": f"{intro}{feat_html}",
            "yourcolor__post_features": [
                {
                    "title": row["title"],
                    "content": row["content"],
                    "icon": CHECK_ICON,
                }
                for row in features
            ],
        },
        "post__work_steps__data": {
            "work_steps__title": generated["steps_title"],
            "work_steps__content": generated["steps_intro"] + steps_html(steps),
            "work_steps_items": [{"title": r["title"], "content": r["content"]} for r in steps],
        },
        "post__price_list__data": {
            "price_list__title": generated["prices_title"],
            "price_list__content": generated["prices_intro"] + prices_html(prices),
            "price_list__table_title1": "البند",
            "price_list__table_title2": "التقدير (ر.ع)",
            "price_list__items": [{"title": r["title"], "value": r["value"]} for r in prices],
        },
        "post__services__data": {
            "services__title": generated["services_title"],
            "services__content": generated["services_intro"] + services_html(services),
            "post_services_items": [
                {"title": r["title"], "content": r["content"], "image": "", "image_id": ""}
                for r in services
            ],
        },
        "post__call_section__data": {
            "call_section_title": generated["call_title"],
            "call_section_content": generated["call_content"],
            "call_section_phone": "",
            "call_section_whatsapp": whatsapp,
        },
        "whatsapp_number": whatsapp,
        "phone_number": "",
        "hide_features__section": "",
        "hide_work_steps": "",
        "hide_services_section": "",
        "hide_price_list__section": "",
        "hide_call_section": "",
    }


def build_flat_meta(generated: dict, mapping: dict) -> dict:
    sc = mapping.get("shortcodes") or {}
    pairs = [
        ("post_features", features_html(generated["features"])),
        ("post_steps", steps_html(generated["steps"])),
        ("post_prices", prices_html(generated["prices"])),
        ("post_services", services_html(generated["services"])),
        ("post_call", generated["call_content"]),
    ]
    out = {}
    for shortcode, html in pairs:
        aliases = (sc.get(shortcode) or {}).get("aliases") or []
        key = aliases[0] if aliases else shortcode
        env_key = {
            "post_features": "FEATURES_META_KEY",
            "post_steps": "STEPS_META_KEY",
            "post_prices": "PRICES_META_KEY",
            "post_services": "SERVICES_META_KEY",
            "post_call": "CALL_META_KEY",
        }[shortcode]
        key = os.environ.get(env_key, key)
        out[key] = html
    return out


def write_post(wp: WP, post_id: int, meta: dict, mode: str) -> tuple[int, Any]:
    if mode == "kayan":
        return wp.post(f"/rukn/v1/article/{post_id}", data={"meta": meta})[:2]
    if mode == "acf":
        return wp.post(f"/wp/v2/posts/{post_id}", data={"acf": meta})[:2]
    return wp.post(f"/wp/v2/posts/{post_id}", data={"meta": meta})[:2]


def load_progress(path: Path) -> dict:
    if not path.is_file():
        return {"processed": {}, "failed": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"processed": {}, "failed": {}}
    data.setdefault("processed", {})
    data.setdefault("failed", {})
    return data


def save_progress(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def append_jsonl(path: Path, row: dict) -> None:
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def inspect_keys(wp: WP, args, mapping: dict) -> None:
    post_id = args.post_id or 0
    log("=== Default Kayan map (scripts/kayan_field_map.json) ===")
    log(json.dumps(mapping.get("shortcodes"), ensure_ascii=False, indent=2))
    if not post_id:
        log("Pass --post-id N to compare against a live post.")
        return
    code, data, _ = wp.get(
        f"/wp/v2/posts/{post_id}",
        context="edit",
        _fields="id,slug,title,meta,content",
    )
    log(f"=== REST GET /wp/v2/posts/{post_id}?context=edit  status={code} ===")
    if isinstance(data, dict):
        title = (data.get("title") or {}).get("raw") or (data.get("title") or {}).get("rendered")
        log(f"title: {title}")
        meta = data.get("meta") if isinstance(data.get("meta"), dict) else {}
        log("registered REST meta keys: " + ", ".join(sorted(meta.keys()) or ["(none)"]))
        kayan = [k for k in meta if k.startswith("post__") or k.startswith("hide_")]
        log("kayan-looking REST keys: " + (", ".join(kayan) if kayan else "(none — expected; Kayan is not show_in_rest)"))
    code2, data2, _ = wp.get(f"/rukn/v1/article/{post_id}")
    log(f"=== GET /rukn/v1/article/{post_id} status={code2} (GET is expected 404; POST is the writer) ===")
    if isinstance(data2, dict):
        log(str(data2)[:400])
    admin_pw = os.environ.get("WP_ADMIN_PASSWORD")
    if not admin_pw:
        log("Set WP_ADMIN_PASSWORD to dump editor input names from post.php.")
        return
    admin = Admin(args.base, os.environ["WP_USER"], admin_pw)
    admin.login()
    html = admin.post_editor_html(post_id)
    names = editor_input_names(html)
    log(f"=== Editor input names ({len(names)}) ===")
    for n in names:
        log("  " + n)
    sample = editor_value(html, "post__features__data[features__title]")
    log("features__title sample: " + (sample[:120] or "(empty)"))
    wa = editor_value(html, "post__call_section__data[call_section_whatsapp]")
    log("call_section_whatsapp sample: " + (wa or "(empty)"))


def write_report(path: Path, stats: dict, errors: list[str], provider: str, mode: str, applied: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Kayan field fill report",
        "",
        f"- time: {utc_now()}",
        f"- provider: {provider}",
        f"- mode: {mode}",
        f"- apply: {applied}",
        "",
        f"- إجمالي المقالات: {stats.get('queued', 0)}",
        f"- تم تحديثه: {stats.get('updated', 0)}",
        f"- تم تخطيه: {stats.get('skipped', 0)}",
        f"- dry-run: {stats.get('dry', 0)}",
        f"- فشل: {stats.get('failed', 0)}",
        "",
        "## أهم الأخطاء",
        "",
    ]
    if errors:
        lines.extend(f"- {e}" for e in errors[:20])
    else:
        lines.append("- لا توجد")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def resolve_write_mode(args, mapping: dict) -> str:
    return (args.write_mode or os.environ.get("WRITE_MODE") or mapping.get("write_mode") or "kayan").lower()


def process(args) -> int:
    load_dotenv(ROOT / ".env")
    mapping = json.loads(DEFAULT_MAP.read_text(encoding="utf-8"))
    user = os.environ.get("WP_USER")
    app = os.environ.get("WP_APP_PASSWORD")
    if not user or not app:
        raise SystemExit("Set WP_USER and WP_APP_PASSWORD (see .env.example)")
    wp = WP(args.base, user, app)
    whatsapp = re.sub(r"\D", "", os.environ.get("WP_WHATSAPP") or WHATSAPP_DEFAULT)
    mode = resolve_write_mode(args, mapping)

    if args.print_map:
        log(json.dumps(mapping, ensure_ascii=False, indent=2))
        return 0

    code, me, _ = wp.get("/wp/v2/users/me", context="edit")
    if code != 200 or not isinstance(me, dict):
        raise SystemExit(f"auth failed {code}: {me}")

    if args.inspect_keys:
        inspect_keys(wp, args, mapping)
        return 0

    provider = "classify" if args.classify_only else pick_provider(args)
    log(f"auth ok user={me.get('slug')} roles={me.get('roles')} provider={provider} mode={mode} apply={args.apply}")

    id_filter = []
    if args.ids:
        id_filter = [int(x.strip()) for x in args.ids.split(",") if x.strip()]
    if args.post_id:
        id_filter.append(int(args.post_id))
    id_filter = list(dict.fromkeys(id_filter))

    posts_raw = []
    cache_path = Path(args.posts_cache) if args.posts_cache else None
    if cache_path and cache_path.is_file() and not id_filter:
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            if isinstance(cached, list) and cached:
                posts_raw = cached
                log(f"loaded posts cache {cache_path} n={len(posts_raw)}")
        except json.JSONDecodeError:
            posts_raw = []
    if not posts_raw:
        posts_raw = fetch_posts(wp, args.wp_delay, only_ids=id_filter or None)
        if cache_path and not id_filter:
            cache_path.write_text(json.dumps(posts_raw, ensure_ascii=False), encoding="utf-8")
            log(f"wrote posts cache {cache_path} n={len(posts_raw)}")
    posts = [unpack_post(p) for p in posts_raw]
    posts.sort(key=lambda p: p["id"])
    if args.offset:
        posts = posts[args.offset :]
    if args.limit and args.limit > 0:
        posts = posts[: args.limit]
    log(f"queued {len(posts)} posts")

    progress = load_progress(Path(args.progress))
    admin = None
    if args.scan_editor and os.environ.get("WP_ADMIN_PASSWORD"):
        admin = Admin(args.base, user, os.environ["WP_ADMIN_PASSWORD"])
        admin.login()

    public_status: dict[int, tuple[bool, str]] = {}
    if args.empty_only and not args.force:
        public_status = classify_public_empty(posts, workers=8)

    stats = {"queued": len(posts), "updated": 0, "skipped": 0, "failed": 0, "dry": 0}

    for i, post in enumerate(posts, 1):
        prefix = f"[{i}/{len(posts)}] id={post['id']} {post['slug']}"
        pid = str(post["id"])
        if (not args.force) and pid in progress.get("processed", {}) and args.resume:
            log(f"{prefix} skip-resume")
            stats["skipped"] += 1
            continue
        if not post["has_shortcodes"] and not args.include_without_shortcodes:
            log(f"{prefix} skip-no-shortcodes")
            stats["skipped"] += 1
            continue

        empty = True
        empty_reason = "assume-empty"
        if args.empty_only and not args.force:
            if post["id"] in public_status:
                empty, empty_reason = public_status[post["id"]]
            elif post["link"]:
                _st, html = fetch_public(post["link"])
                empty = public_is_empty(html)
                empty_reason = "public-leftover-shortcodes" if empty else "public-expanded"
            if admin is not None:
                sleep_delay(args.wp_delay)
                ed = admin.post_editor_html(post["id"])
                title_val = editor_value(ed, "post__features__data[features__title]")
                if title_val:
                    empty = False
                    empty_reason = "editor-features-title-filled"
                else:
                    empty = True
                    empty_reason = "editor-features-title-empty"
        if args.empty_only and not args.force and not empty:
            log(f"{prefix} skip-filled ({empty_reason})")
            stats["skipped"] += 1
            continue

        if args.classify_only:
            log(f"{prefix} EMPTY {empty_reason}")
            stats["dry"] += 1
            append_jsonl(Path(args.log_file), {"ts": utc_now(), "id": post["id"], "status": "empty", "empty_reason": empty_reason, "title": post["title"]})
            continue

        try:
            generated = generate_fields(provider, post, args, whatsapp)
        except Exception as e:
            log(f"{prefix} FAIL llm: {e}")
            stats["failed"] += 1
            progress["failed"][pid] = {"error": str(e), "ts": utc_now()}
            save_progress(Path(args.progress), progress)
            append_jsonl(Path(args.log_file), {"ts": utc_now(), "id": post["id"], "status": "llm-fail", "error": str(e)})
            sleep_delay(args.llm_delay)
            continue

        meta = build_kayan_meta(generated, whatsapp) if mode == "kayan" else build_flat_meta(generated, mapping)
        preview = {
            "features_title": generated["features_title"],
            "steps_title": generated["steps_title"],
            "prices_title": generated["prices_title"],
            "call_title": generated["call_title"],
            "city": generated.get("city_ar") or post["city_ar"],
        }
        if not args.apply:
            log(f"{prefix} DRY-RUN {empty_reason} {json.dumps(preview, ensure_ascii=False)}")
            if args.dump_payload:
                log(json.dumps(meta, ensure_ascii=False, indent=2)[:4000])
            stats["dry"] += 1
            append_jsonl(
                Path(args.log_file),
                {"ts": utc_now(), "id": post["id"], "status": "dry-run", "preview": preview, "empty_reason": empty_reason},
            )
            sleep_delay(args.llm_delay)
            continue

        sleep_delay(args.wp_delay)
        code, resp = write_post(wp, post["id"], meta, mode)
        if code in {200, 201} and (not isinstance(resp, dict) or resp.get("ok") is not False):
            log(f"{prefix} UPDATED {empty_reason} {preview['features_title']}")
            stats["updated"] += 1
            progress["processed"][pid] = {"ts": utc_now(), "title": post["title"], "preview": preview}
            progress.get("failed", {}).pop(pid, None)
            append_jsonl(Path(args.log_file), {"ts": utc_now(), "id": post["id"], "status": "updated", "preview": preview})
        else:
            log(f"{prefix} FAIL write {code} {str(resp)[:240]}")
            stats["failed"] += 1
            progress["failed"][pid] = {"error": str(resp)[:400], "code": code, "ts": utc_now()}
            append_jsonl(Path(args.log_file), {"ts": utc_now(), "id": post["id"], "status": "write-fail", "code": code})
        save_progress(Path(args.progress), progress)
        sleep_delay(args.llm_delay)

    errors = []
    failed_map = progress.get("failed") or {}
    for pid, info in list(failed_map.items())[:20]:
        errors.append(f"id={pid}: {info.get('error') or info.get('code') or info}")
    write_report(Path(args.report), stats, errors, provider, mode, args.apply)
    log("done " + json.dumps(stats))
    log("report " + args.report)
    return 0 if stats["failed"] == 0 else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Fill Kayan [post_*] metaboxes from post titles via LLM.")
    p.add_argument("--base", default=os.environ.get("WP_BASE", DEFAULT_BASE))
    p.add_argument("--apply", action="store_true", help="Write to WordPress. Default is dry-run.")
    p.add_argument("--dry-run", action="store_true", help="Explicit dry-run (default).")
    p.add_argument("--offline", action="store_true", help="Skip LLM; use local Arabic templates.")
    p.add_argument("--provider", default=None, help="auto|openai|gemini|offline")
    p.add_argument("--openai-model", default=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"))
    p.add_argument("--gemini-model", default=os.environ.get("GEMINI_MODEL", "gemini-2.0-flash"))
    p.add_argument("--write-mode", default=None, help="kayan (default) | acf | core")
    p.add_argument("--empty-only", dest="empty_only", action="store_true", default=True, help="Skip posts whose shortcodes already expand (default).")
    p.add_argument("--no-empty-only", dest="empty_only", action="store_false", help="Queue filled posts too (still needs --force to overwrite).")
    p.add_argument("--force", action="store_true", help="Overwrite even if fields look filled.")
    p.add_argument("--include-without-shortcodes", action="store_true")
    p.add_argument("--scan-editor", action="store_true", help="Use wp-admin HTML to decide empty vs filled.")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--ids", default="", help="Comma-separated post IDs")
    p.add_argument("--post-id", type=int, default=0)
    p.add_argument("--llm-delay", type=float, default=1.2)
    p.add_argument("--wp-delay", type=float, default=0.35)
    p.add_argument("--progress", default=str(DEFAULT_PROGRESS))
    p.add_argument("--log-file", default=str(DEFAULT_LOG))
    p.add_argument("--report", default=str(ROOT / "docs" / "kayan-fill-report.md"))
    p.add_argument("--resume", action="store_true", help="Skip IDs already in the progress file.")
    p.add_argument("--inspect-keys", action="store_true")
    p.add_argument("--print-map", action="store_true")
    p.add_argument("--dump-payload", action="store_true")
    p.add_argument("--classify-only", action="store_true", help="List empty vs filled posts without calling an LLM.")
    p.add_argument("--posts-cache", default="/tmp/kayan-posts-cache.json", help="JSON cache of WP post list.")
    p.add_argument("--self-test", action="store_true", help="Generate one offline payload and exit.")
    return p


def self_test() -> int:
    post = {
        "id": 1204,
        "slug": "wooden-arbor-al-buraimi",
        "title": "شركة تركيب عرائش خشبية في البريمي",
        "service_ar": "تركيب عرائش خشبية",
        "city_ar": "البريمي",
        "service": "wooden-arbor",
        "city": "al-buraimi",
        "link": "",
        "raw": "[post_features]",
        "has_shortcodes": True,
    }
    gen = offline_generate(post, WHATSAPP_DEFAULT)
    meta = build_kayan_meta(gen, WHATSAPP_DEFAULT)
    assert len(meta["post__features__data"]["yourcolor__post_features"]) == 4
    assert CHECK_ICON in meta["post__features__data"]["features__content"]
    assert TABLE_HEAD_STYLE in meta["post__price_list__data"]["price_list__content"]
    assert TOOLS_ICON in meta["post__services__data"]["services__content"]
    assert meta["post__call_section__data"]["call_section_phone"] == ""
    assert meta["post__call_section__data"]["call_section_whatsapp"] == WHATSAPP_DEFAULT
    assert "البريمي" in meta["post__call_section__data"]["call_section_content"]
    assert all(r["value"] == "يُحدد بعد المعاينة" for r in gen["prices"])
    assert not re.search(r"\d", json.dumps(gen["prices"], ensure_ascii=False))
    log("self-test ok")
    log(json.dumps({
        "features_title": gen["features_title"],
        "n_steps": len(gen["steps"]),
        "n_prices": len(gen["prices"]),
        "call": gen["call_content"][:120],
    }, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    load_dotenv(ROOT / ".env")
    parser = build_parser()
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.apply and args.dry_run:
        raise SystemExit("Use either --apply or --dry-run, not both")
    args.apply = bool(args.apply)
    return process(args)


if __name__ == "__main__":
    sys.exit(main())
