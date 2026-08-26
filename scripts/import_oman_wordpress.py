#!/usr/bin/env python3
"""Import Oman CSV articles + Kayan services/cities into rukn-eltatawer.com/om.

Credentials come from the environment (never committed):
  WP_USER            WordPress username
  WP_APP_PASSWORD    WordPress application password
  WP_BASE            Optional, default https://www.rukn-eltatawer.com/om
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

csv.field_size_limit(sys.maxsize)

DEFAULT_BASE = "https://www.rukn-eltatawer.com/om"
WHATSAPP = os.environ.get("WP_WHATSAPP", "971586634710")
PHONE = os.environ.get("WP_PHONE", "+971586634710")

CITIES = [
    {"name": "مسقط", "slug": "muscat", "prep": "بمسقط"},
    {"name": "صلالة", "slug": "salalah", "prep": "بصلالة"},
    {"name": "نزوى", "slug": "nizwa", "prep": "بنزوى"},
    {"name": "صحار", "slug": "sohar", "prep": "بصحار"},
    {"name": "صور", "slug": "sur", "prep": "بصور"},
    {"name": "البريمي", "slug": "al-buraimi", "prep": "بالبريمي"},
    {"name": "عبري", "slug": "ibri", "prep": "بعبري"},
    {"name": "الرستاق", "slug": "rustaq", "prep": "بالرستاق"},
]

SERVICES = [
    (
        "water-leak-detection",
        "كشف تسربات المياه",
        "تحديد دقيق لمصدر التسرب بدون تكسير.",
        ["كاميرا حرارية متطورة", "بدون تكسير", "تقرير مصوّر مفصّل", "إصلاح بعد التشخيص"],
    ),
    (
        "roof-insulation",
        "عزل الأسطح",
        "حماية من الحرارة وتسرب المياه.",
        ["عزل فوم بولي يوريثان", "أغشية بيتومينية معدّلة", "طلاء عازل للحرارة", "عزل خزانات وحمامات"],
    ),
    (
        "thermal-waterproof-insulation",
        "العزل المائي والحراري",
        "حلول عزل متكاملة للمباني والخزانات في مناخ عُمان.",
        ["عزل مائي للأسطح", "عزل حراري للأسقف", "معالجة الرطوبة", "ضمان مكتوب حسب الخامة"],
    ),
    (
        "general-maintenance",
        "الصيانة العامة",
        "صيانة شاملة للمنازل والمنشآت بفريق واحد.",
        ["إصلاحات يومية", "صيانة دورية", "معالجة الأعطال", "تقرير بعد الزيارة"],
    ),
    (
        "building-maintenance",
        "صيانة المباني",
        "صيانة شاملة للمباني والمنشآت.",
        ["صيانة مباني", "معالجة الشروخ", "ترميم وتجديد", "عقود صيانة دورية"],
    ),
    (
        "plumbing",
        "أعمال السباكة",
        "إصلاح وتركيب الأدوات الصحية وشبكات المياه.",
        ["إصلاح تسربات الأنابيب", "تركيب الأدوات الصحية", "فحص شبكات المياه", "صيانة مضخات"],
    ),
    (
        "sewer-clearing",
        "تسليك المجاري",
        "تسليك احترافي بالضغط والمعدات الحديثة.",
        ["تسليك بالضغط", "معالجة الانسدادات", "فحص الخطوط", "منع تكرار المشكلة"],
    ),
    (
        "electrical-works",
        "أعمال الكهرباء",
        "تمديدات وإصلاح أعطال الإنارة واللوحات.",
        ["تمديدات كهربائية", "إصلاح الأعطال", "لوحات وأفياش", "فحص سلامة التوصيل"],
    ),
    (
        "ac-install-maintenance",
        "تركيب وصيانة التكييف",
        "تنظيف وصيانة وتركيب المكيفات.",
        ["تنظيف وصيانة المكيفات", "شحن الفريون", "تركيب وحدات جديدة", "إصلاح الأعطال"],
    ),
    (
        "cleaning-sterilization",
        "التنظيف والتعقيم",
        "نظافة عميقة لكل المساحات بمواد آمنة.",
        ["تنظيف عميق شامل", "تنظيف الخزانات", "تعقيم بالبخار", "مواد آمنة"],
    ),
    (
        "pest-control",
        "مكافحة الحشرات",
        "إبادة آمنة مع متابعة بعد التنفيذ.",
        ["مكافحة الصراصير والنمل", "مكافحة القوارض", "مواد آمنة", "متابعة بعد التنفيذ"],
    ),
    (
        "landscaping",
        "تنسيق الحدائق",
        "تصميم وتنفيذ المساحات الخارجية.",
        ["تصميم الحدائق", "عشب طبيعي وصناعي", "شبكات ري", "صيانة دورية"],
    ),
    (
        "swimming-pools",
        "إنشاء وصيانة المسابح",
        "إنشاء وصيانة المسابح والنوافير.",
        ["إنشاء مسابح", "صيانة دورية", "نوافير وشلالات", "معالجة المياه"],
    ),
    (
        "painting",
        "الصبغ والدهانات",
        "صبغ داخلي وخارجي بتشطيب نظيف.",
        ["صبغ داخلي وخارجي", "معالجة الجدران", "دهانات مقاومة", "تشطيبات نهائية"],
    ),
    (
        "gypsum-board",
        "تركيب الجبس بورد",
        "أسقف وديكورات جبس بورد حسب المخطط.",
        ["أسقف معلقة", "قواطع جبسية", "إضاءة مخفية", "تشطيب دقيق"],
    ),
    (
        "interior-design",
        "تصميم وتنفيذ الديكورات",
        "تشطيب داخلي بلمسة نظيفة.",
        ["تصميم داخلي", "تنفيذ الديكورات", "تنسيق الخامات", "تسليم بعد المعاينة"],
    ),
]

FAQS = [
    (
        "هل تكشفون التسرب بدون تكسير؟",
        "نعم. نستخدم كاميرا حرارية وأجهزة كشف لتحديد مصدر التسرب بدقة قبل أي تكسير، وتستلم تقريراً مصوراً يوضح الموقع والسبب.",
    ),
    (
        "ما المدن التي تغطونها في سلطنة عُمان؟",
        "نغطي مسقط، صلالة، نزوى، صحار، صور، البريمي، عبري، والرستاق.",
    ),
    (
        "هل تقدمون كل الخدمات أم تخصص واحد؟",
        "نغطي كشف التسربات والعزل والصيانة العامة والسباكة والتكييف والتنظيف ومكافحة الحشرات وتنسيق الحدائق والمسابح والصبغ والديكورات.",
    ),
    (
        "هل يوجد ضمان على العمل؟",
        "نعم، ويختلف حسب نوع الخدمة والخامة المستخدمة — ويُوضَّح لك مكتوباً في عرض السعر قبل البدء.",
    ),
    (
        "كم تستغرق مدة التنفيذ؟",
        "تُحدَّد بعد المعاينة حسب حجم العمل، وتكون مكتوبة في عرض السعر.",
    ),
    (
        "هل المعاينة قبل التسعير؟",
        "نعم — لا نسعّر عبر الهاتف. الفني يعاين الموقع ويشخّص المشكلة، ثم تستلم عرض سعر واضح.",
    ),
    (
        "كيف أطلب الخدمة؟",
        "تواصل عبر واتساب أو الاتصال، ونرد لتحديد موعد المعاينة.",
    ),
]

CTX = ssl.create_default_context()


class WP:
    def __init__(self, base: str, user: str, app_password: str):
        self.base = base.rstrip("/")
        token = base64.b64encode(f"{user}:{app_password}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {token}",
            "User-Agent": "RuknOmanImporter/1.0",
            "Accept": "application/json",
        }

    def url(self, route: str, **query) -> str:
        q = {"rest_route": route}
        q.update(query)
        return self.base + "/index.php?" + urllib.parse.urlencode(q)

    def request(self, method: str, route: str, data=None, query=None, raw_body=None, extra_headers=None):
        headers = dict(self.headers)
        if extra_headers:
            headers.update(extra_headers)
        body = raw_body
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
            with urllib.request.urlopen(req, context=CTX, timeout=120) as resp:
                raw = resp.read()
                return resp.status, json.loads(raw) if raw else {}, dict(resp.headers)
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", "replace")
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                parsed = {"message": raw[:500], "status": e.code}
            return e.code, parsed, dict(e.headers)

    def get(self, route: str, **query):
        return self.request("GET", route, query=query)

    def post(self, route: str, data=None, **query):
        return self.request("POST", route, data=data, query=query)

    def delete(self, route: str, **query):
        return self.request("DELETE", route, query=query)


def load_csv(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            content = (row.get("post_content") or "").replace("\x00", "").rstrip()
            if not content:
                continue
            row = dict(row)
            row["post_content"] = content
            rows.append(row)
    return rows


def adapt_city(text: str, src_city: dict, dst_city: dict) -> str:
    pairs = [
        (src_city["prep"], dst_city["prep"]),
        (src_city["name"], dst_city["name"]),
        (src_city["slug"], dst_city["slug"]),
    ]
    for old, new in pairs:
        text = text.replace(old, new)
    return text


def reconstruct_missing(rows: list[dict]) -> list[dict]:
    by_slug = {r["post_name"]: r for r in rows}
    template = by_slug.get("glass-facade-cleaning-muscat")
    if not template:
        return rows
    src_city = next(c for c in CITIES if c["slug"] == "muscat")
    needed = [
        ("glass-facade-cleaning-ibri", "عبري", "ibri"),
        ("glass-facade-cleaning-rustaq", "الرستاق", "rustaq"),
        ("glass-facade-cleaning-al-buraimi", "البريمي", "al-buraimi"),
    ]
    out = [r for r in rows if r["post_name"] != "glass-facade-cleaning-ibri"]
    for slug, emirate, city_slug in needed:
        dst = next(c for c in CITIES if c["slug"] == city_slug)
        existing = by_slug.get(slug)
        if existing and len(existing["post_content"]) > 7000:
            out.append(existing)
            continue
        row = dict(template)
        row["emirate"] = emirate
        row["post_name"] = slug
        row["post_title"] = adapt_city(template["post_title"], src_city, dst)
        row["rank_math_title"] = adapt_city(template["rank_math_title"], src_city, dst)
        row["rank_math_description"] = adapt_city(template["rank_math_description"], src_city, dst)
        row["tags"] = adapt_city(template["tags"], src_city, dst)
        row["post_content"] = adapt_city(template["post_content"], src_city, dst)
        out.append(row)
    return out


def rewrite_content(html: str, image_url: str) -> str:
    html = html.replace("{PHONE_RUKN_OMAN}", PHONE)
    html = html.replace("{WHATSAPP_RUKN_OMAN}", WHATSAPP)

    def repl(match: re.Match) -> str:
        tag = match.group(0)
        tag = re.sub(r'\ssrc="[^"]+"', f' src="{image_url}"', tag)
        if "class=" not in tag:
            tag = tag.replace("<img ", '<img class="rukn-service-img" ')
        return tag

    return re.sub(r"<img\b[^>]*>", repl, html, flags=re.I)


def make_cover_jpeg(title: str) -> bytes:
    from PIL import Image, ImageDraw, ImageFont

    try:
        import arabic_reshaper
        from bidi.algorithm import get_display

        def rtl(s: str) -> str:
            return get_display(arabic_reshaper.reshape(s))
    except Exception:
        def rtl(s: str) -> str:
            return s

    w, h = 1280, 720
    img = Image.new("RGB", (w, h), "#0A1F4E")
    draw = ImageDraw.Draw(img)
    for i in range(h):
        mix = i / h
        r = int(10 + 20 * mix)
        g = int(31 + 40 * mix)
        b = int(78 + 60 * mix)
        draw.line([(0, i), (w, i)], fill=(r, g, b))
    draw.rectangle([48, 48, w - 48, h - 48], outline="#4FA8FF", width=4)
    font_path = "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Bold.ttf"
    brand = ImageFont.truetype(font_path, 42)
    body = ImageFont.truetype(font_path, 54)
    draw.text((w // 2, 220), rtl("ركن التطور — عُمان"), font=brand, fill="#F5C542", anchor="mm")
    draw.text((w // 2, 370), rtl(title), font=body, fill="white", anchor="mm")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=86)
    return buf.getvalue()


def get_or_create_term(wp: WP, taxonomy_route: str, name: str, slug: str | None = None) -> int:
    query = {"per_page": 100, "search": name}
    code, data, _ = wp.get(taxonomy_route, **query)
    if code == 200 and isinstance(data, list):
        for term in data:
            if term.get("name") == name or (slug and term.get("slug") == slug):
                return int(term["id"])
    payload = {"name": name}
    if slug:
        payload["slug"] = slug
    code, data, _ = wp.post(taxonomy_route, payload)
    if code in (200, 201):
        return int(data["id"])
    if isinstance(data, dict) and data.get("data", {}).get("term_id"):
        return int(data["data"]["term_id"])
    raise RuntimeError(f"term {name!r} failed {code}: {data}")


def existing_by_slug(wp: WP, route: str, slug: str) -> dict | None:
    code, data, _ = wp.get(route, slug=slug, status="any", per_page=20)
    if code != 200 or not isinstance(data, list):
        return None
    for item in data:
        if item.get("slug") == slug:
            return item
    return None


def upload_jpeg(wp: WP, filename: str, blob: bytes, alt: str) -> tuple[int, str]:
    code, data, _ = wp.request(
        "POST",
        "/wp/v2/media",
        raw_body=blob,
        extra_headers={
            "Content-Type": "image/jpeg",
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )
    if code not in (200, 201):
        raise RuntimeError(f"media upload failed {code}: {data}")
    media_id = int(data["id"])
    src = data.get("source_url") or ""
    wp.request("POST", f"/wp/v2/media/{media_id}", data={"alt_text": alt, "title": alt})
    return media_id, src


def service_html(title: str, lead: str, bullets: list[str]) -> str:
    items = "".join(f"<li>{b}</li>" for b in bullets)
    return f"""
<p>{lead} فريق ركن التطور في سلطنة عُمان يبدأ بالمعاينة والتشخيص، ثم يقدّم عرض سعر مكتوب قبل التنفيذ.</p>
<ul>{items}</ul>
<p>التغطية تشمل مسقط وصلالة ونزوى وصحار وصور والبريمي وعبري والرستاق. تواصل معنا عبر واتساب لتحديد موعد المعاينة.</p>
""".strip()


def import_all(csv_path: Path, status: str, delay: float) -> None:
    user = os.environ.get("WP_USER")
    password = os.environ.get("WP_APP_PASSWORD")
    if not user or not password:
        raise SystemExit("Set WP_USER and WP_APP_PASSWORD")
    wp = WP(os.environ.get("WP_BASE", DEFAULT_BASE), user, password)

    code, me, _ = wp.get("/wp/v2/users/me", context="edit")
    if code != 200:
        raise SystemExit(f"auth failed {code}: {me}")
    print(f"authenticated as {me.get('slug')} roles={me.get('roles')}")

    wp.post("/wp/v2/settings", {"description": "الخدمات المنزلية المتكاملة في سلطنة عُمان — كشف تسربات، عزل، صيانة، تنظيف ومكافحة حشرات."})

    city_ids = []
    city_id_by_name = {}
    for city in CITIES:
        tid = get_or_create_term(wp, "/wp/v2/cities", city["name"], city["slug"])
        city_ids.append(tid)
        city_id_by_name[city["name"]] = tid
        print(f"city {city['name']} -> {tid}")

    category_ids = {}
    for name, slug in [
        ("كشف تسربات المياه", "leak-detection"),
        ("العزل", "insulation"),
        ("الصيانة العامة", "general-maintenance"),
        ("السباكة والتسليك", "plumbing"),
        ("التكييف والكهرباء", "ac-electrical"),
        ("خدمات التنظيف", "cleaning-services"),
        ("مكافحة الحشرات", "pest-control"),
        ("الحدائق والمسابح", "gardens-pools"),
        ("الصبغ والديكورات", "painting-decor"),
    ]:
        category_ids[slug] = get_or_create_term(wp, "/wp/v2/service_categories", name, slug)
        print("service category", name, category_ids[slug])
    service_cat_map = {
        "water-leak-detection": "leak-detection",
        "roof-insulation": "insulation",
        "thermal-waterproof-insulation": "insulation",
        "general-maintenance": "general-maintenance",
        "building-maintenance": "general-maintenance",
        "plumbing": "plumbing",
        "sewer-clearing": "plumbing",
        "electrical-works": "ac-electrical",
        "ac-install-maintenance": "ac-electrical",
        "cleaning-sterilization": "cleaning-services",
        "pest-control": "pest-control",
        "landscaping": "gardens-pools",
        "swimming-pools": "gardens-pools",
        "painting": "painting-decor",
        "gypsum-board": "painting-decor",
        "interior-design": "painting-decor",
    }

    cover_cache: dict[str, tuple[int, str]] = {}
    default_cover = make_cover_jpeg("خدمات ركن التطور")
    default_id, default_src = upload_jpeg(wp, "rukn-oman-cover.jpg", default_cover, "ركن التطور عمان")
    cover_cache["__default__"] = (default_id, default_src)
    print("default cover", default_id, default_src)

    for slug, title, lead, bullets in SERVICES:
        existing = existing_by_slug(wp, "/wp/v2/services", slug)
        payload = {
            "title": title,
            "slug": slug,
            "status": "publish",
            "excerpt": lead,
            "content": service_html(title, lead, bullets),
            "cities": city_ids,
            "service_categories": [category_ids[service_cat_map[slug]]] if slug in service_cat_map else [],
            "featured_media": default_id,
        }
        if existing:
            code, data, _ = wp.post(f"/wp/v2/services/{existing['id']}", payload)
            print(f"service update {slug} {code} id={data.get('id')}")
        else:
            code, data, _ = wp.post("/wp/v2/services", payload)
            print(f"service create {slug} {code} id={data.get('id')}")
        time.sleep(delay)

    for question, answer in FAQS:
        slug = "faq-" + hashlib.sha1(question.encode()).hexdigest()[:12]
        existing = existing_by_slug(wp, "/wp/v2/faqs", slug)
        payload = {"title": question, "slug": slug, "status": "publish", "content": f"<p>{answer}</p>"}
        if existing:
            wp.post(f"/wp/v2/faqs/{existing['id']}", payload)
        else:
            # avoid duplicate titles
            code, found, _ = wp.get("/wp/v2/faqs", search=question, per_page=10, status="any")
            if code == 200 and any(x.get("title", {}).get("rendered") == question for x in found or []):
                continue
            code, data, _ = wp.post("/wp/v2/faqs", payload)
            print(f"faq {code} {question[:40]}")
        time.sleep(delay)

    rows = reconstruct_missing(load_csv(csv_path))
    print("csv rows", len(rows))

    tag_ids: dict[str, int] = {}

    def tags_for(row: dict) -> list[int]:
        names = [t.strip() for t in (row.get("tags") or "").split(",") if t.strip()]
        if row.get("categories"):
            names.append(row["categories"].strip())
        ids = []
        for name in names:
            if name not in tag_ids:
                tag_ids[name] = get_or_create_term(wp, "/wp/v2/tags", name)
            ids.append(tag_ids[name])
        return ids

    created = updated = skipped = failed = 0
    for i, row in enumerate(rows, 1):
        slug = row["post_name"].strip()
        title = row["post_title"].strip()
        city_name = (row.get("emirate") or "").strip()
        cities = [city_id_by_name[city_name]] if city_name in city_id_by_name else []
        type_key = slug
        for city in sorted((c["slug"] for c in CITIES), key=len, reverse=True):
            suffix = "-" + city
            if slug.endswith(suffix):
                type_key = slug[: -len(suffix)]
                break
        if type_key not in cover_cache:
            blob = make_cover_jpeg(title.split(" ب")[0] if " ب" in title else title)
            mid, src = upload_jpeg(wp, f"{type_key}.jpg", blob, title)
            cover_cache[type_key] = (mid, src)
        media_id, image_url = cover_cache[type_key]
        content = rewrite_content(row["post_content"], image_url)
        payload = {
            "title": title,
            "slug": slug,
            "status": status,
            "content": content,
            "excerpt": (row.get("rank_math_description") or "")[:180],
            "tags": tags_for(row),
            "cities": cities,
            "featured_media": media_id,
            "comment_status": "closed",
        }
        existing = existing_by_slug(wp, "/wp/v2/posts", slug)
        try:
            if existing:
                if existing.get("id") == 1:
                    skipped += 1
                    continue
                code, data, _ = wp.post(f"/wp/v2/posts/{existing['id']}", payload)
                action = "update"
            else:
                code, data, _ = wp.post("/wp/v2/posts", payload)
                action = "create"
            if code in (200, 201):
                created += action == "create"
                updated += action == "update"
                print(f"[{i}/{len(rows)}] {action} {code} {slug} id={data.get('id')}")
            else:
                failed += 1
                print(f"[{i}/{len(rows)}] FAIL {code} {slug} {data}")
        except Exception as exc:
            failed += 1
            print(f"[{i}/{len(rows)}] ERROR {slug} {exc}")
        time.sleep(delay)

    hello = existing_by_slug(wp, "/wp/v2/posts", "hello-world")
    if hello:
        code, data, _ = wp.delete(f"/wp/v2/posts/{hello['id']}", force="true")
        print("deleted hello-world", code)

    print(json.dumps({"created": created, "updated": updated, "skipped": skipped, "failed": failed, "total": len(rows)}, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="rukn-eltatawer-oman-FULL.csv.oplusdownload")
    parser.add_argument("--status", default="publish", choices=["publish", "draft"])
    parser.add_argument("--delay", type=float, default=0.15)
    args = parser.parse_args()
    csv_path = Path(args.csv)
    if not csv_path.is_file():
        raise SystemExit(f"CSV not found: {csv_path}")
    import_all(csv_path, args.status, args.delay)


if __name__ == "__main__":
    main()
