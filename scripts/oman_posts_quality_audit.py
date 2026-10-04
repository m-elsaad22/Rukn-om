#!/usr/bin/env python3
"""Live quality audit of published Rukn Oman articles.

Answers:
  1. posts under 1000 words
  2. same-template articles
  3. similar / near-duplicate articles
  4. content that does not match title, topic, or service
  5. errors and gaps

Credentials from the environment (never committed):
  WP_USER, WP_APP_PASSWORD, WP_BASE (default https://rukn-eltatawer.com/om)
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import html as htmlmod
import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CTX = ssl.create_default_context()
DEFAULT_BASE = "https://rukn-eltatawer.com/om"
THIN_RAW = 1000
BOILER_DOC_SHARE = 0.08
NEAR_DUP_HAMMING = 8
TEMPLATE_FAMILY_MIN = 8

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

# Homepage / advertised Oman families. Anything else is off-scope for the live brand.
IN_SCOPE_HINTS = (
    "leak", "تسرب", "عزل", "insul", "waterproof", "thermal", "humidity",
    "plumb", "sewer", "drain", "septic", "tank", "heater", "pump", "filter",
    "ac-", "air-", "freon", "duct", "cool", "split", "central-ac", "window-ac",
    "electric", "elec", "light", "panel",
    "clean", "steril", "disinfect", "ozone", "steam", "chlorine",
    "pest", "ant-", "cockroach", "rodent", "termite", "mosquito", "flea",
    "bed-bug", "lizard", "snake", "scorpion", "pigeon", "bird",
    "garden", "landscap", "grass", "pool", "irrigation", "palm", "pergola",
    "arbor", "fountain", "waterfall",
    "paint", "صبغ", "دهان", "gypsum", "decor", "plaster", "wallpaper",
    "marble", "ceramic", "floor", "parquet", "vinyl", "stone",
    "maintenance", "renovation", "repair", "crack", "building", "villa-inspection",
    "carpenter", "blacksmith", "doors", "windows", "kitchen", "bathroom",
    "annex", "majlis", "fence", "brick", "interlock",
)

OFF_SCOPE_HINTS = (
    "shipping", "freight", "parcel", "cargo", "piano-moving", "furniture-moving",
    "furniture-storage", "indoor-moving", "outdoor-moving", "car-shipping",
    "satellite", "sat-dish", "cctv", "elevator", "solar",
)

TOKEN_AR: dict[str, tuple[str, ...]] = {
    "cleaning": ("تنظيف",),
    "clean": ("تنظيف",),
    "washing": ("غسيل", "تنظيف"),
    "sterilization": ("تعقيم", "تنظيف"),
    "disinfection": ("تعقيم", "تطهير"),
    "ozone": ("أوزون", "تعقيم"),
    "steam": ("بخار", "تعقيم"),
    "chlorine": ("كلور", "تعقيم"),
    "leak": ("تسرب", "تسريب"),
    "detection": ("كشف", "تسرب"),
    "insulation": ("عزل",),
    "waterproofing": ("عزل", "مائي"),
    "waterproof": ("عزل", "مائي"),
    "thermal": ("عزل", "حرار"),
    "humidity": ("رطوب", "عزل"),
    "plumbing": ("سباك", "سباكة"),
    "plumber": ("سباك", "سباكة"),
    "sewer": ("مجاري", "تسليك"),
    "drain": ("تسليك", "مجاري"),
    "drainage": ("صرف", "تسليك"),
    "septic": ("تحليل", "صرف"),
    "electrical": ("كهرب",),
    "electric": ("كهرب",),
    "electrician": ("كهرب",),
    "elec": ("كهرب",),
    "wiring": ("تمديد", "كهرب"),
    "lighting": ("إنارة", "كهرب"),
    "panel": ("لوحة", "كهرب"),
    "ac": ("تكييف", "مكيف"),
    "freon": ("فريون", "تكييف"),
    "duct": ("دكت", "تكييف"),
    "split": ("سبليت", "تكييف"),
    "cooling": ("تبريد", "تكييف"),
    "pest": ("مكافحة", "حشرات"),
    "cockroach": ("صراصير", "مكافحة"),
    "ant": ("نمل", "مكافحة"),
    "rodent": ("قوارض", "مكافحة"),
    "termite": ("نمل أبيض", "مكافحة"),
    "mosquito": ("ناموس", "مكافحة"),
    "flea": ("براغيث", "مكافحة"),
    "lizard": ("وزغ", "مكافحة"),
    "snake": ("ثعابين", "مكافحة"),
    "scorpion": ("عقارب", "مكافحة"),
    "pigeon": ("حمام", "مكافحة"),
    "bird": ("طيور", "مكافحة"),
    "landscaping": ("حدائق", "تنسيق"),
    "garden": ("حدائق", "حديقة"),
    "grass": ("عشب", "حدائق"),
    "irrigation": ("ري", "حدائق"),
    "palm": ("نخيل", "حدائق"),
    "pergola": ("برجولة", "حدائق"),
    "arbor": ("عريش", "عرائش"),
    "pool": ("مسبح", "مسابح"),
    "painting": ("دهان", "صبغ"),
    "paint": ("دهان", "صبغ"),
    "painter": ("دهان", "صبغ"),
    "gypsum": ("جبس",),
    "decor": ("ديكور",),
    "wallpaper": ("ورق حائط", "ديكور"),
    "plastering": ("لياسة", "بلاستر"),
    "marble": ("رخام",),
    "ceramic": ("سيراميك",),
    "parquet": ("باركيه",),
    "vinyl": ("فينيل",),
    "floor": ("أرضيات",),
    "stone": ("حجر",),
    "maintenance": ("صيانة",),
    "renovation": ("ترميم",),
    "repair": ("إصلاح",),
    "crack": ("شروخ", "ترميم"),
    "building": ("مباني", "صيانة"),
    "shipping": ("شحن",),
    "freight": ("شحن",),
    "moving": ("نقل",),
    "cargo": ("شحن",),
    "parcel": ("طرود", "شحن"),
    "solar": ("طاقة شمسية", "شمسي"),
    "cctv": ("كاميرات", "مراقبة"),
    "elevator": ("مصعد", "مصاعد"),
    "satellite": ("ستالايت", "قمر"),
    "sat": ("ستالايت",),
    "kitchen": ("مطبخ", "مطابخ"),
    "bathroom": ("حمام", "حمامات"),
    "tank": ("خزان", "خزانات"),
    "heater": ("سخان",),
    "pump": ("مضخة", "مضخات"),
    "filter": ("فلتر", "فلاتر"),
    "carpet": ("سجاد",),
    "moquette": ("موكيت",),
    "sofa": ("كنب",),
    "curtain": ("ستائر",),
    "mattress": ("مراتب",),
    "home": ("منزل", "بيوت"),
    "villa": ("فيلا", "فلل"),
    "apartment": ("شقق", "شقة"),
    "office": ("مكاتب",),
    "palace": ("قصور",),
    "majlis": ("مجلس", "مجالس"),
    "hospital": ("مستشف",),
    "school": ("مدارس",),
    "mall": ("مول", "مجمع"),
}

# Distinctive family markers used to catch cross-topic contamination.
FAMILY_MARKERS: dict[str, tuple[str, ...]] = {
    "leak": ("تسرب", "تسريب", "كاميرا حرارية"),
    "insulation": ("عزل", "فوم", "بيتومين"),
    "plumbing": ("سباكة", "سباك", "مجاري", "تسليك", "أنابيب"),
    "electrical": ("كهربائي", "كهرباء", "لوحة كهرب"),
    "ac": ("تكييف", "مكيف", "فريون", "سبليت"),
    "cleaning": ("تنظيف", "تعقيم", "غسيل"),
    "pest": ("مكافحة", "حشرات", "صراصير", "قوارض"),
    "garden": ("حدائق", "عشب", "تنسيق", "مسبح"),
    "paint": ("دهان", "صبغ", "طلاء", "بوية"),
    "shipping": ("شحن", "نقل عفش", "حاوية"),
}

SLUG_FAMILY: list[tuple[str, tuple[str, ...]]] = [
    (("leak", "humidity"), "leak"),
    (("insul", "waterproof", "thermal", "tank-lining", "soundproof"), "insulation"),
    (("plumb", "sewer", "drain", "septic", "sanitary", "heater", "pump", "filter", "ro-plants"), "plumbing"),
    (("electric", "elec", "lighting", "panel", "wiring"), "electrical"),
    (("ac-", "freon", "duct", "split", "cooling", "window-ac", "central-ac", "air-purification", "solar-ac"), "ac"),
    (("clean", "steril", "disinfect", "ozone", "steam", "chlorine", "polishing"), "cleaning"),
    (("pest", "ant-", "cockroach", "rodent", "termite", "mosquito", "flea", "bed-bug", "lizard", "snake", "scorpion", "pigeon", "bird"), "pest"),
    (("garden", "landscap", "grass", "pool", "irrigation", "palm", "pergola", "arbor", "fountain", "waterfall", "shades"), "garden"),
    (("paint", "صبغ", "gypsum", "decor", "plaster", "wallpaper", "marble", "ceramic", "floor", "parquet", "vinyl"), "paint"),
    (("shipping", "freight", "parcel", "cargo", "moving", "storage"), "shipping"),
]

PLACEHOLDERS = re.compile(
    r"lorem ipsum|dummy text|your title here|نص تجريبي|اكتب هنا|coming soon|\bTODO\b|\bTBD\b|"
    r"\{PHONE|_RUKN_OMAN\}|\{\{[a-z_]+\}\}|xxx+|placeholder",
    re.I,
)
KAYAN_SHORTCODES = re.compile(r"\[post_[a-z_]+\]")
UAE_LEAK = re.compile(r"الإمارات|إمارات|درهم|دبي|أبوظبي|ابوظبي|الشارقة|عجمان|الفجيرة")
EMIRATE_WORD = re.compile(r"إمارة|امارة")
INCOMPLETE = re.compile(r"(تغطية حسب الاتفاق:\s*(</p>|$)|حسب الاتفاق:\s*<)")
TAG_RE = re.compile(r"<[^>]+>", re.S)
SCRIPT_RE = re.compile(r"<(script|style|noscript)[^>]*>.*?</\1>", re.I | re.S)
HEADING_RE = re.compile(r"<h([1-6])\b[^>]*>(.*?)</h\1>", re.I | re.S)
SENT_SPLIT = re.compile(r"(?<=[\.!?؟。\n])\s+")

HEAD_PATTERNS = [
    (re.compile(r"هل تحتاج إلى"), "CTA_NEED"),
    (re.compile(r"مناسبة لحالتك"), "FIT"),
    (re.compile(r"التأجيل سيكلف"), "DELAY"),
    (re.compile(r"اكتفيت بالترقيع"), "PATCH"),
    (re.compile(r"قراءة المشكلة"), "DIAG"),
    (re.compile(r"حدود الحل المنزلي"), "DIY"),
    (re.compile(r"ما الذي لا ننصح"), "AVOID"),
    (re.compile(r"كيف تسير الزيارة"), "VISIT"),
    (re.compile(r"^معاينة"), "SURVEY"),
    (re.compile(r"العمل داخل"), "WORK_IN"),
    (re.compile(r"تعريف .+ كما"), "DEFINE"),
    (re.compile(r"ما الذي يتغير بعد"), "AFTER"),
    (re.compile(r"ترتيب الزيارة"), "SCHEDULE"),
    (re.compile(r"كيف تختلف الأحياء"), "AREAS"),
    (re.compile(r"علامات أن"), "SIGNS"),
    (re.compile(r"تشغيل .+ داخل"), "OPS"),
    (re.compile(r"مميزات شركة"), "FEATURES"),
    (re.compile(r"ماذا تتوقع من التنفيذ"), "EXPECT"),
    (re.compile(r"لماذا لا تكفي العدة"), "TOOLS"),
    (re.compile(r"^طلب شركة"), "REQUEST"),
]


class WP:
    def __init__(self, base: str, user: str, app_password: str):
        self.base = base.rstrip("/")
        token = base64.b64encode(f"{user}:{app_password}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {token}",
            "User-Agent": "RuknPostsQualityAudit/1.0",
            "Accept": "application/json",
        }

    def get(self, route: str, **query):
        q = {"rest_route": route}
        q.update({k: v for k, v in query.items() if v is not None})
        url = self.base + "/index.php?" + urllib.parse.urlencode(q)
        req = urllib.request.Request(url, headers=self.headers, method="GET")
        try:
            with urllib.request.urlopen(req, context=CTX, timeout=180) as resp:
                text = resp.read().decode("utf-8", "replace")
                start = min([i for i in (text.find("{"), text.find("[")) if i >= 0], default=-1)
                parsed, _ = json.JSONDecoder().raw_decode(text[start:]) if start >= 0 else ({}, 0)
                return resp.status, parsed, dict(resp.headers)
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", "replace")
            return e.code, {"message": raw[:400]}, dict(e.headers)
        except (TimeoutError, OSError) as e:
            return 599, {"message": str(e)[:200]}, {}


def strip_html(html: str) -> str:
    text = SCRIPT_RE.sub(" ", html or "")
    text = htmlmod.unescape(TAG_RE.sub(" ", text))
    return re.sub(r"\s+", " ", text).strip()


def words_of(text: str) -> list[str]:
    return re.findall(r"\S+", text)


def headings(html: str) -> list[tuple[int, str]]:
    return [(int(m.group(1)), strip_html(m.group(2))) for m in HEADING_RE.finditer(html or "")]


def split_slug(slug: str) -> tuple[str, str]:
    slug = (slug or "").strip("/")
    for city in sorted(CITIES, key=len, reverse=True):
        suffix = "-" + city
        if slug.endswith(suffix):
            return slug[: -len(suffix)], city
    return slug, ""


def service_family(service: str) -> str:
    s = service or ""
    for hints, fam in SLUG_FAMILY:
        if any(h in s for h in hints):
            return fam
    return "other"


def service_terms(service: str) -> tuple[str, ...]:
    bits = [p for p in (service or "").split("-") if p not in {"and", "or", "the", "new", "old"}]
    terms: list[str] = []
    for bit in bits:
        terms.extend(TOKEN_AR.get(bit, ()))
    # keep order, unique
    seen = set()
    out = []
    for t in terms:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return tuple(out)


def city_from_title(title: str) -> str:
    for ar, slug in sorted(CITY_ALIASES.items(), key=lambda kv: -len(kv[0])):
        if ar in title:
            return slug
    return ""


def normalize_heading(text: str) -> str:
    t = text
    for ar in CITY_ALIASES:
        t = t.replace(ar, "{CITY}")
    t = re.sub(r"شركة\s+.+?\s+في\s+\{CITY\}", "شركة {SERVICE} في {CITY}", t)
    t = re.sub(r"\d+", "{N}", t)
    return re.sub(r"\s+", " ", t).strip()


def normalize_sentence(text: str) -> str:
    t = re.sub(r"\s+", " ", text).strip()
    if len(t) < 18:
        return ""
    for ar in CITY_ALIASES:
        t = t.replace(ar, "{CITY}")
    t = re.sub(r"\d+", "{N}", t)
    t = re.sub(r"https?://\S+", "{URL}", t)
    return t


def simhash64(tokens: list[str]) -> int:
    if not tokens:
        return 0
    acc = [0] * 64
    for tok in tokens:
        h = int(hashlib.md5(tok.encode("utf-8", "replace")).hexdigest(), 16)
        for i in range(64):
            acc[i] += 1 if (h >> i) & 1 else -1
    out = 0
    for i, v in enumerate(acc):
        if v >= 0:
            out |= 1 << i
    return out


def hamming(a: int, b: int) -> int:
    return (a ^ b).bit_count()


def in_scope(service: str) -> bool:
    s = service or ""
    if any(h in s for h in OFF_SCOPE_HINTS):
        return False
    return any(h in s for h in IN_SCOPE_HINTS) or not s


def fetch_page(wp: WP, route: str, page: int) -> tuple[int, list, dict]:
    fields = "id,slug,link,title,content,excerpt,type,featured_media,cities,service_categories"
    code, data, hdrs = wp.get(
        route,
        status="publish",
        per_page=100,
        page=page,
        _fields=fields,
    )
    if code != 200 or not isinstance(data, list):
        return code, [], hdrs
    return code, data, hdrs


def fetch_all(wp: WP, route: str) -> list[dict]:
    code, first, hdrs = fetch_page(wp, route, 1)
    if code != 200:
        print("fetch fail", route, code, str(first)[:200], flush=True)
        return []
    items = list(first)
    pages = int(hdrs.get("X-WP-TotalPages") or hdrs.get("x-wp-totalpages") or 1)
    print(f"fetched {route} page 1/{pages} (+{len(first)})", flush=True)
    if pages <= 1:
        return items
    with ThreadPoolExecutor(max_workers=4) as pool:
        futs = {pool.submit(fetch_page, wp, route, p): p for p in range(2, pages + 1)}
        for fut in as_completed(futs):
            p = futs[fut]
            _code, data, _h = fut.result()
            items.extend(data)
            print(f"fetched {route} page {p}/{pages} (+{len(data)}) total {len(items)}", flush=True)
    return items


def unpack(item: dict, ptype: str) -> dict:
    title = item.get("title") or {}
    content = item.get("content") or {}
    excerpt = item.get("excerpt") or {}
    html = content.get("rendered") or content.get("raw") or ""
    title_txt = strip_html(title.get("rendered") or title.get("raw") or "")
    excerpt_txt = strip_html(excerpt.get("rendered") or excerpt.get("raw") or "")
    slug = item.get("slug") or ""
    service, city = split_slug(slug)
    heads = headings(html)
    text = strip_html(html)
    wds = words_of(text)
    sents = [s.strip() for s in SENT_SPLIT.split(text) if len(s.strip()) >= 18]
    norm_heads = [normalize_heading(h) for _lvl, h in heads]
    patterns = []
    for h in norm_heads:
        hit = "OTHER"
        for rx, name in HEAD_PATTERNS:
            if rx.search(h):
                hit = name
                break
        patterns.append(hit)
    skeleton = ">".join(patterns) if patterns else ""
    return {
        "id": item.get("id"),
        "type": item.get("type") or ptype,
        "slug": slug,
        "url": item.get("link") or f"{DEFAULT_BASE}/{slug}/",
        "title": title_txt,
        "html": html,
        "text": text,
        "excerpt": excerpt_txt,
        "words": wds,
        "word_count": len(wds),
        "sentences": sents,
        "heads": heads,
        "norm_heads": norm_heads,
        "h1": sum(1 for lvl, _ in heads if lvl == 1),
        "h2": sum(1 for lvl, _ in heads if lvl == 2),
        "h3": sum(1 for lvl, _ in heads if lvl == 3),
        "skeleton": skeleton,
        "skeleton_hash": hashlib.md5(skeleton.encode("utf-8")).hexdigest()[:12] if skeleton else "",
        "service": service,
        "family": service_family(service),
        "in_scope": in_scope(service) if ptype == "post" else True,
        "city": city,
        "cities_tax": item.get("cities") or [],
        "cats_tax": item.get("service_categories") or [],
        "featured": int(item.get("featured_media") or 0),
    }


def analyze(docs: list[dict]) -> tuple[list[dict], list[dict], dict]:
    posts = [d for d in docs if d["type"] == "post"]
    n = max(len(posts), 1)
    sent_docs: Counter[str] = Counter()
    for d in posts:
        seen = set()
        for s in d["sentences"]:
            ns = normalize_sentence(s)
            if ns and ns not in seen:
                seen.add(ns)
                sent_docs[ns] += 1

    boiler = {s for s, c in sent_docs.items() if c >= max(3, int(n * BOILER_DOC_SHARE))}
    for s in list(sent_docs):
        if any(
            k in s
            for k in (
                "هل تحتاج إلى شركة",
                "قراءة المشكلة في بيوت",
                "مناسبة لحالتك",
                "اكتفيت بالترقيع",
                "التأجيل سيكلف",
                "كيف تختلف الأحياء",
                "لماذا لا تكفي العدة",
            )
        ):
            boiler.add(s)

    fam_count = Counter(d["skeleton_hash"] for d in posts if d["skeleton_hash"])
    for d in docs:
        boiler_sents = [s for s in d["sentences"] if normalize_sentence(s) in boiler]
        boiler_words = sum(len(words_of(s)) for s in boiler_sents)
        unique_words = max(d["word_count"] - boiler_words, 0)
        ratio = (boiler_words / d["word_count"]) if d["word_count"] else 1.0
        tokens = [w.lower() for w in d["words"] if len(w) > 2 and w not in CITY_ALIASES]
        d["simhash"] = simhash64(tokens[::2][:1200])
        d["boilerplate_ratio"] = round(ratio, 3)
        d["unique_word_count"] = unique_words
        d["template_family_size"] = fam_count.get(d["skeleton_hash"], 0) if d["type"] == "post" else 0

    buckets: dict[int, list[int]] = defaultdict(list)
    post_idxs = [i for i, d in enumerate(docs) if d["type"] == "post"]
    for i in post_idxs:
        buckets[docs[i]["simhash"] >> 48].append(i)
    pairs: list[dict] = []
    seen_pairs = set()
    for idxs in buckets.values():
        for a in range(len(idxs)):
            for b in range(a + 1, len(idxs)):
                i, j = idxs[a], idxs[b]
                dist = hamming(docs[i]["simhash"], docs[j]["simhash"])
                if dist > NEAR_DUP_HAMMING:
                    continue
                key = (min(docs[i]["id"], docs[j]["id"]), max(docs[i]["id"], docs[j]["id"]))
                if key in seen_pairs:
                    continue
                seen_pairs.add(key)
                same_svc = docs[i]["service"] == docs[j]["service"] and bool(docs[i]["service"])
                pairs.append(
                    {
                        "id_a": docs[i]["id"],
                        "url_a": docs[i]["url"],
                        "title_a": docs[i]["title"],
                        "id_b": docs[j]["id"],
                        "url_b": docs[j]["url"],
                        "title_b": docs[j]["title"],
                        "hamming": dist,
                        "same_service": same_svc,
                        "kind": (
                            "city-variant-template"
                            if same_svc and docs[i]["city"] != docs[j]["city"]
                            else ("cross-service-duplicate" if not same_svc else "near-duplicate")
                        ),
                    }
                )
    pair_index: dict[int, list[dict]] = defaultdict(list)
    for p in pairs:
        pair_index[p["id_a"]].append(p)
        pair_index[p["id_b"]].append(p)

    featured_count = Counter(d["featured"] for d in posts)
    rows = []
    for d in docs:
        issues: list[str] = []
        notes: list[str] = []
        html = d["html"]
        text = d["text"]
        title = d["title"]

        if d["word_count"] < THIN_RAW:
            issues.append("thin_raw")
            notes.append(f"عدد الكلمات {d['word_count']} أقل من {THIN_RAW}.")

        if d["type"] == "post" and (
            d["boilerplate_ratio"] >= 0.35
            or (d["template_family_size"] >= TEMPLATE_FAMILY_MIN and d["word_count"] >= 400)
        ):
            issues.append("template_boilerplate")
            notes.append(
                f"هيكل H2 مكرر على {d['template_family_size']} مقالة، ونسبة جمل القالب {d['boilerplate_ratio']:.0%}."
            )

        related = pair_index.get(d["id"], []) if d["type"] == "post" else []
        if related:
            best = min(related, key=lambda p: p["hamming"])
            other = best["url_b"] if best["id_a"] == d["id"] else best["url_a"]
            issues.append("duplicate_similar")
            notes.append(f"تشابه مرتفع (hamming={best['hamming']}, {best['kind']}) مع {other}.")
            d["similar_to"] = other
            d["similarity_kind"] = best["kind"]
            d["hamming"] = best["hamming"]
        else:
            d["similar_to"] = ""
            d["similarity_kind"] = ""
            d["hamming"] = ""

        slug_city = d["city"]
        title_city = city_from_title(title)
        if d["type"] == "post" and slug_city and title_city and slug_city != title_city:
            issues.append("intent_mismatch")
            notes.append(f"المدينة في العنوان ({CITIES.get(title_city, title_city)}) تختلف عن الرابط ({CITIES.get(slug_city, slug_city)}).")
        if d["type"] == "post" and slug_city:
            ar = CITIES[slug_city]
            others = {k: v for k, v in CITIES.items() if k != slug_city}
            own = text.count(ar)
            rival = max(((text.count(v), k) for k, v in others.items()), default=(0, ""))
            if own == 0:
                issues.append("intent_mismatch")
                notes.append(f"المحتوى لا يذكر مدينة الرابط «{ar}».")
            elif rival[0] >= own + 3 and rival[0] >= 4:
                issues.append("intent_mismatch")
                notes.append(f"المحتوى يكرر «{CITIES[rival[1]]}» ({rival[0]}) أكثر من «{ar}» ({own}).")

        terms = service_terms(d["service"]) if d["type"] == "post" else ()
        if terms:
            hits = [t for t in terms if t in text or t in title]
            need = 1 if len(terms) <= 2 else max(1, len(terms) // 2)
            if len(hits) < need and d["word_count"] > 80:
                issues.append("intent_mismatch")
                notes.append(f"كلمات الخدمة المتوقعة ناقصة: {', '.join(terms)} (وُجد: {', '.join(hits) or 'لا شيء'}).")

        if d["type"] == "post" and d["family"] in FAMILY_MARKERS:
            own_marks = FAMILY_MARKERS[d["family"]]
            own_score = sum(text.count(m) for m in own_marks)
            rival_scores = []
            for fam, marks in FAMILY_MARKERS.items():
                if fam == d["family"]:
                    continue
                score = sum(text.count(m) for m in marks)
                rival_scores.append((score, fam))
            rival_scores.sort(reverse=True)
            if rival_scores and rival_scores[0][0] >= max(own_score + 8, 12) and own_score < 4:
                issues.append("intent_mismatch")
                notes.append(
                    f"المحتوى يميل لخدمة «{rival_scores[0][1]}» ({rival_scores[0][0]}) أكثر من خدمة المقال «{d['family']}» ({own_score})."
                )

        if d["type"] == "post" and not d["in_scope"]:
            issues.append("intent_mismatch")
            notes.append("الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة شمسية).")

        if d["type"] == "post" and title and text:
            title_tokens = [w for w in re.findall(r"[\u0600-\u06FFa-zA-Z]{3,}", title)]
            overlap = sum(1 for w in title_tokens if w in text)
            if title_tokens and overlap / len(title_tokens) < 0.35:
                issues.append("intent_mismatch")
                notes.append("جسم المقال لا يعيد أغلب كلمات العنوان.")

        shorts = sorted(set(KAYAN_SHORTCODES.findall(html)))
        if shorts:
            issues.append("unexpanded_shortcodes")
            notes.append("شورت كود كيان ظاهر للزائر: " + ", ".join(shorts[:6]) + ".")
        if d["h2"] == 0 and d["word_count"] > 250 and d["slug"] not in {"html-sitemap", "en-home"}:
            issues.append("missing_headings")
            notes.append("لا توجد عناوين H2 رغم طول النص.")
        ph = PLACEHOLDERS.findall(html + " " + title + " " + d["excerpt"])
        if ph:
            issues.append("placeholder")
            notes.append("عناصر نائبة: " + ", ".join(sorted(set(ph))[:6]))
        uae = UAE_LEAK.findall(text + title)
        if uae:
            issues.append("uae_leak")
            notes.append("كلمات إماراتية متبقية: " + ", ".join(sorted(set(uae))[:5]))
        emirate = EMIRATE_WORD.findall(text + title)
        if emirate and "محافظ" not in text:
            issues.append("uae_leak")
            notes.append("استخدام «إمارة» في سياق عُمان.")
        if INCOMPLETE.search(html) or d["excerpt"].rstrip().endswith(":") or "تغطية حسب الاتفاق:" in (d["excerpt"] + text[:400]):
            issues.append("incomplete")
            notes.append("عبارة ناقصة «تغطية حسب الاتفاق:» بلا تكملة.")
        if d["type"] == "post" and not d["cities_tax"]:
            issues.append("missing_tax")
            notes.append("المقالة غير مربوطة بتصنيف المدن.")
        if d["type"] == "post" and not d["cats_tax"]:
            issues.append("missing_tax")
            notes.append("المقالة غير مربوطة بتصنيف الخدمات.")
        if d["type"] == "post" and d["featured"] in (0,):
            issues.append("missing_image")
            notes.append("لا توجد صورة بارزة.")
        elif d["type"] == "post" and featured_count.get(d["featured"], 0) >= 50:
            issues.append("shared_image")
            notes.append(f"صورة بارزة مكررة على {featured_count[d['featured']]} مقالة (id={d['featured']}).")
        if re.search(r"<h2[^>]*>\s*</h2>", html, re.I):
            issues.append("structural_error")
            notes.append("عنوان H2 فارغ.")
        paras = [strip_html(p) for p in re.findall(r"<p\b[^>]*>(.*?)</p>", html, flags=re.I | re.S)]
        paras = [p for p in paras if len(p) > 80]
        if len(paras) >= 2 and any(paras[i] == paras[i + 1] for i in range(len(paras) - 1)):
            issues.append("structural_error")
            notes.append("فقرتان متتاليتان متطابقتان.")

        issue_set = []
        for flag in issues:
            if flag not in issue_set:
                issue_set.append(flag)

        cats = []
        for flag, label in (
            ("thin_raw", "أقل من 1000 كلمة"),
            ("template_boilerplate", "نفس القالب"),
            ("duplicate_similar", "متشابهة"),
            ("intent_mismatch", "لا تناسب الموضوع/الخدمة"),
            ("unexpanded_shortcodes", "أخطاء أو نواقص"),
            ("missing_headings", "أخطاء أو نواقص"),
            ("placeholder", "أخطاء أو نواقص"),
            ("uae_leak", "أخطاء أو نواقص"),
            ("incomplete", "أخطاء أو نواقص"),
            ("missing_tax", "أخطاء أو نواقص"),
            ("missing_image", "أخطاء أو نواقص"),
            ("shared_image", "أخطاء أو نواقص"),
            ("structural_error", "أخطاء أو نواقص"),
        ):
            if flag in issue_set and label not in cats:
                cats.append(label)

        rows.append(
            {
                "id": d["id"],
                "type": d["type"],
                "title": d["title"],
                "url": d["url"],
                "slug": d["slug"],
                "service": d["service"],
                "family": d["family"],
                "in_scope": "yes" if d["in_scope"] else "no",
                "city": d["city"],
                "word_count": d["word_count"],
                "unique_word_count": d["unique_word_count"],
                "boilerplate_ratio": d["boilerplate_ratio"],
                "h2": d["h2"],
                "template_family_size": d["template_family_size"],
                "skeleton_hash": d["skeleton_hash"],
                "similar_to": d["similar_to"],
                "similarity_kind": d["similarity_kind"],
                "hamming": d["hamming"],
                "featured": d["featured"],
                "issue_flags": "|".join(issue_set),
                "issue_categories": " | ".join(cats) if cats else "سليمة",
                "primary_issue": cats[0] if cats else "سليمة",
                "observations": " ".join(notes) if notes else "لا توجد ملاحظات جوهرية.",
            }
        )

    stats = {
        "docs": len(docs),
        "posts": len(posts),
        "boiler_sentences": len(boiler),
        "pairs": len(pairs),
        "fam_count": fam_count,
        "featured_count": featured_count,
        "off_scope": sum(1 for d in posts if not d["in_scope"]),
    }
    return rows, pairs, stats


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow(row)


def md_table(rows: list[dict], cols: list[tuple[str, str]], limit: int = 25) -> str:
    if not rows:
        return "_لا توجد نتائج في هذه الفئة._\n"
    header = "| " + " | ".join(c[1] for c in cols) + " |"
    sep = "| " + " | ".join("---" for _ in cols) + " |"
    lines = [header, sep]
    for row in rows[:limit]:
        vals = []
        for key, _label in cols:
            val = str(row.get(key, "")).replace("|", "/").replace("\n", " ")
            if key in {"title", "observations", "url", "similar_to"} and len(val) > 140:
                val = val[:137] + "..."
            vals.append(val)
        lines.append("| " + " | ".join(vals) + " |")
    extra = len(rows) - limit
    if extra > 0:
        lines.append(f"\n_{extra} صفاً إضافياً في ملف CSV._")
    return "\n".join(lines) + "\n"


def write_markdown(path: Path, rows: list[dict], pairs: list[dict], stats: dict) -> None:
    posts = [r for r in rows if r["type"] == "post"]
    pages = [r for r in rows if r["type"] != "post"]
    thin_posts = [r for r in posts if "أقل من 1000 كلمة" in r["issue_categories"]]
    thin_other = [r for r in pages if "أقل من 1000 كلمة" in r["issue_categories"]]
    templ = [r for r in posts if "نفس القالب" in r["issue_categories"]]
    dup = [r for r in posts if "متشابهة" in r["issue_categories"]]
    intent = [r for r in posts if "لا تناسب الموضوع/الخدمة" in r["issue_categories"]]
    errors = [r for r in posts if "أخطاء أو نواقص" in r["issue_categories"]]
    wc = sorted(r["word_count"] for r in posts)
    median = wc[len(wc) // 2] if wc else 0
    mn, mx = (wc[0], wc[-1]) if wc else (0, 0)
    fams = [(h, c) for h, c in stats["fam_count"].most_common(12) if h]
    top_image = stats["featured_count"].most_common(5)
    cross = [p for p in pairs if p["kind"] == "cross-service-duplicate"]
    cityv = [p for p in pairs if p["kind"] == "city-variant-template"]
    off = [r for r in posts if r["in_scope"] == "no"]

    flag_n = Counter()
    for r in posts:
        for f in (r.get("issue_flags") or "").split("|"):
            if f:
                flag_n[f] += 1

    cols = [
        ("title", "العنوان"),
        ("url", "الرابط"),
        ("word_count", "كلمات"),
        ("unique_word_count", "كلمات فريدة"),
        ("city", "المدينة"),
        ("observations", "الملاحظة"),
    ]

    md = []
    md.append("# فحص جودة مقالات موقع عُمان")
    md.append("")
    md.append("المصدر: المقالات المنشورة حالياً على `https://rukn-eltatawer.com/om` عبر ووردبريس REST.")
    md.append(f"تاريخ الفحص: 4 أكتوبر 2026. المقالات المفحوصة: **{len(posts)}**. الصفحات وأنواع الخدمات: **{len(pages)}**.")
    md.append("")
    md.append("## الخلاصة")
    md.append("")
    md.append("| البند | العدد |")
    md.append("| --- | --- |")
    md.append(f"| مقالات منشورة | {len(posts)} |")
    md.append(f"| وسيط عدد الكلمات | {median} (من {mn} إلى {mx}) |")
    md.append(f"| أقل من 1000 كلمة (مقالات) | {len(thin_posts)} |")
    md.append(f"| أقل من 1000 كلمة (صفحات/خدمات كيان) | {len(thin_other)} |")
    md.append(f"| مكتوبة بنفس القالب | {len(templ)} |")
    md.append(f"| متشابهة / شبه مكررة | {len(dup)} |")
    md.append(f"| لا تناسب الموضوع أو الخدمة | {len(intent)} |")
    md.append(f"| أخطاء أو نواقص | {len(errors)} |")
    md.append(f"| أزواج شبه مكررة | {len(pairs)} |")
    md.append(f"| خدمات خارج نطاق الموقع المعلن | {stats['off_scope']} |")
    md.append("")
    md.append("### كيف حُسبت النتائج")
    md.append("")
    md.append("- **الكلمات**: الرموز بعد حذف HTML، مفصولة بمسافات. هذا مقياس «أقل من 1000 كلمة» كما يظهر للزائر.")
    md.append("- **نفس القالب**: تسلسل عناوين H2 بعد استبدال اسم المدينة/الخدمة، أو نسبة جمل القالب ≥ 35%.")
    md.append("- **التشابه**: simhash 64-بت بعد حذف أسماء المدن. Hamming ≤ 8 يعني شبه تطابق.")
    md.append("- **عدم التناسب**: مدينة العنوان ≠ الرابط، غياب كلمات الخدمة، سيطرة موضوع خدمة أخرى، أو خدمة خارج نطاق الصفحة الرئيسية.")
    md.append("- **النواقص**: شورت كود ظاهر، بقايا إمارات، عبارة ناقصة، تصنيف مفقود، صورة مكررة، فقرات متطابقة.")
    md.append("")
    md.append("## 1) المقالات أقل من 1000 كلمة")
    md.append("")
    if not thin_posts:
        md.append("لا توجد مقالة خدمة منشورة تحت 1000 كلمة. الوسيط حوالي ألفي كلمة لأن مولّد كيان يملأ قالباً طويلاً.")
        md.append("")
    md.append(md_table(sorted(thin_posts, key=lambda r: r["word_count"]), cols, 40))
    md.append("صفحات المحاور وخدمات كيان القصيرة (ليست مقالات):")
    md.append("")
    md.append(md_table(sorted(thin_other, key=lambda r: r["word_count"]), cols, 30))
    md.append("## 2) المقالات المكتوبة بنفس القالب")
    md.append("")
    md.append("أكبر عائلات هيكل H2:")
    md.append("")
    md.append("| بصمة الهيكل | عدد المقالات |")
    md.append("| --- | --- |")
    for h, c in fams:
        md.append(f"| `{h}` | {c} |")
    md.append("")
    md.append(
        f"هذا هو الخطر الأكبر: **{len(templ)}** مقالة تشارك هيكل كيان نفسه "
        "(معاينة / مناسبة لحالتك / الترقيع / التأجيل سيكلف / كيف تختلف الأحياء…). "
        "الطول كبير، لكن التميّز ضعيف، والمدن الثماني لنفس الخدمة تبدو مقالاً واحداً مع استبدال اسم المدينة."
    )
    md.append("")
    md.append(md_table(sorted(templ, key=lambda r: r["boilerplate_ratio"], reverse=True), cols, 25))
    md.append("## 3) المقالات المتشابهة")
    md.append("")
    md.append(f"أزواج شبه مكررة: **{len(pairs)}** — منها {len(cityv)} نسخة مدينة لنفس الخدمة، و{len(cross)} تشابه بين خدمتين مختلفتين.")
    md.append("")
    pair_cols = [
        ("kind", "النوع"),
        ("hamming", "المسافة"),
        ("title_a", "عنوان أ"),
        ("url_a", "رابط أ"),
        ("title_b", "عنوان ب"),
        ("url_b", "رابط ب"),
    ]
    md.append("### تشابه بين خدمتين مختلفتين (أعلى خطورة)")
    md.append("")
    md.append(md_table(sorted(cross, key=lambda p: p["hamming"]), pair_cols, 40))
    md.append("### نفس الخدمة في مدن مختلفة (نسخ مدينة)")
    md.append("")
    md.append(md_table(sorted(cityv, key=lambda p: p["hamming"]), pair_cols, 20))
    md.append("## 4) مقالات لا يتناسب محتواها مع العنوان أو الموضوع أو الخدمة")
    md.append("")
    md.append(md_table(sorted(intent, key=lambda r: r["service"]), cols, 50))
    if off:
        svc_n = Counter(r["service"] for r in off)
        md.append("خدمات خارج نطاق الصفحة الرئيسية (شحن، نقل، ستالايت، كاميرات، مصاعد، طاقة شمسية):")
        md.append("")
        md.append(", ".join(f"`{s}` ×{c}" for s, c in svc_n.most_common(40)))
        md.append("")
    md.append("## 5) الأخطاء والنواقص")
    md.append("")
    md.append("| نوع النقص | مقالات |")
    md.append("| --- | --- |")
    labels = [
        ("unexpanded_shortcodes", "شورت كود ظاهر"),
        ("incomplete", "عبارة ناقصة"),
        ("uae_leak", "بقايا إمارات"),
        ("missing_tax", "تصنيف مدينة/خدمة مفقود"),
        ("missing_image", "بدون صورة بارزة"),
        ("shared_image", "صورة بارزة مكررة"),
        ("structural_error", "خطأ هيكلي"),
        ("placeholder", "نص نائب"),
        ("missing_headings", "بدون H2"),
    ]
    for key, label in labels:
        md.append(f"| {label} | {flag_n.get(key, 0)} |")
    md.append("")
    md.append("أكثر الصور البارزة تكراراً:")
    md.append("")
    md.append("| رقم الصورة | عدد المقالات |")
    md.append("| --- | --- |")
    for mid, c in top_image:
        md.append(f"| {mid} | {c} |")
    md.append("")
    md.append(md_table(sorted(errors, key=lambda r: r["word_count"]), cols, 40))
    md.append("## التوصيات")
    md.append("")
    md.append("1. لا تكتب مقالات جديدة الآن. الكمية كافية؛ المشكلة في التكرار لا في النقص العددي.")
    md.append("2. أعد كتابة المقدمة وFAQ والدليل المحلي لكل خدمة×مدينة حتى لا تبقى الثماني المدن نسخة واحدة.")
    md.append("3. ادمج أو فرّق المقالات المتشابهة عبر خدمتين مختلفتين (Hamming منخفض).")
    md.append("4. احذف أو حوّل خدمات الشحن/النقل/الستالايت/المصاعد إن لم تقدموها فعلياً في عُمان.")
    md.append("5. أكمل عبارة «تغطية حسب الاتفاق:» بصورة بارزة خاصة بكل خدمة، لا صورة واحدة لكل الموقع.")
    md.append("6. صفحتا `/services/{slug}/` والمحاور (من نحن، المدن، اتصل بنا) قصيرة ويجب إغناؤها أو عدم فهرستها كمنافس للمقالات.")
    md.append("")
    md.append("التفاصيل الكاملة: `docs/oman-posts-quality-audit.csv` و`docs/oman-posts-quality-audit-pairs.csv`.")
    md.append("")
    path.write_text("\n".join(md), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default=os.environ.get("WP_BASE", DEFAULT_BASE))
    parser.add_argument("--out-dir", default=str(ROOT / "docs"))
    parser.add_argument("--cache", default="/tmp/rukn-posts-quality-cache.json")
    args = parser.parse_args()

    cache_path = Path(args.cache)
    raw_items = []
    if cache_path.is_file():
        print("loading cache", cache_path, flush=True)
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
        raw_items = payload["items"]
    else:
        user = os.environ.get("WP_USER")
        app = os.environ.get("WP_APP_PASSWORD")
        if not user or not app:
            raise SystemExit("Set WP_USER and WP_APP_PASSWORD")
        wp = WP(args.base, user, app)
        code, me, _ = wp.get("/wp/v2/users/me")
        if code != 200 or not isinstance(me, dict):
            raise SystemExit(f"auth failed {code}: {me}")
        print("auth", me.get("slug"), flush=True)
        bundled = []
        for route, ptype in (
            ("/wp/v2/posts", "post"),
            ("/wp/v2/pages", "page"),
            ("/wp/v2/services", "services"),
        ):
            for item in fetch_all(wp, route):
                bundled.append({"item": item, "ptype": ptype})
        cache_path.write_text(json.dumps({"items": bundled}, ensure_ascii=False), encoding="utf-8")
        print("cached", cache_path, "bytes", cache_path.stat().st_size, flush=True)
        raw_items = bundled

    docs = [unpack(rec["item"], rec["ptype"]) for rec in raw_items]
    posts = [d for d in docs if d["type"] == "post"]
    print(
        "unpacked",
        len(docs),
        "posts",
        len(posts),
        "median words",
        sorted(d["word_count"] for d in posts)[len(posts) // 2] if posts else 0,
        flush=True,
    )
    rows, pairs, stats = analyze(docs)
    out = Path(args.out_dir)
    fields = [
        "id",
        "type",
        "title",
        "url",
        "slug",
        "service",
        "family",
        "in_scope",
        "city",
        "word_count",
        "unique_word_count",
        "boilerplate_ratio",
        "h2",
        "template_family_size",
        "skeleton_hash",
        "similar_to",
        "similarity_kind",
        "hamming",
        "featured",
        "issue_flags",
        "issue_categories",
        "primary_issue",
        "observations",
    ]
    write_csv(out / "oman-posts-quality-audit.csv", rows, fields)
    write_csv(
        out / "oman-posts-quality-audit-pairs.csv",
        sorted(pairs, key=lambda p: (p["kind"], p["hamming"])),
        ["kind", "hamming", "id_a", "title_a", "url_a", "id_b", "title_b", "url_b", "same_service"],
    )
    write_markdown(out / "oman-posts-quality-audit.md", rows, pairs, stats)
    print("wrote", out / "oman-posts-quality-audit.md", flush=True)
    print(
        "posts flagged",
        sum(1 for r in rows if r["type"] == "post" and r["issue_categories"] != "سليمة"),
        "/",
        sum(1 for r in rows if r["type"] == "post"),
        flush=True,
    )


if __name__ == "__main__":
    main()
