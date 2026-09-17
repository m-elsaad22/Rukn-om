#!/usr/bin/env python3
"""Deep content + on-page SEO audit of published Rukn Oman URLs via WP REST.

Reads live published posts, pages and services. Writes:
  docs/content-seo-audit.csv
  docs/content-seo-audit-pairs.csv
  docs/content-seo-audit.md

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
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CTX = ssl.create_default_context()
DEFAULT_BASE = "https://rukn-eltatawer.com/om"
THIN_RAW = 1000
THIN_UNIQUE = 450
BOILER_DOC_SHARE = 0.08
NEAR_DUP_HAMMING = 8
TEMPLATE_FAMILY_MIN = 6

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

# Expected topical tokens for the service slug (Arabic). Missing most of these => intent mismatch.
SERVICE_TERMS: dict[str, tuple[str, ...]] = {
    "home-cleaning": ("تنظيف", "منزل", "بيوت"),
    "apartment-cleaning": ("تنظيف", "شقق", "شقة"),
    "villa-cleaning": ("تنظيف", "فيلل", "فيلا"),
    "palace-cleaning": ("تنظيف", "قصور", "قصر"),
    "office-cleaning": ("تنظيف", "مكاتب", "مكتب"),
    "majlis-cleaning": ("تنظيف", "مجلس", "مجالس"),
    "school-nursery-cleaning": ("تنظيف", "مدارس", "حضانة"),
    "hospital-clinic-cleaning": ("تنظيف", "مستشف", "عياد"),
    "mall-cleaning": ("تنظيف", "مجمع", "مول"),
    "pool-cleaning": ("مسابح", "مسبح", "برك"),
    "kitchen-cleaning": ("مطبخ", "مطابخ", "تنظيف"),
    "bathroom-cleaning": ("حمام", "حمامات", "دورة"),
    "water-tank-cleaning": ("خزان", "خزانات", "مياه"),
    "diesel-tank-cleaning": ("ديزل", "خزان", "وقود"),
    "carpet-cleaning": ("سجاد", "موكيت", "تنظيف"),
    "moquette-cleaning": ("موكيت", "سجاد"),
    "sofa-cleaning": ("كنب", "أرائك", "تنجيد"),
    "curtain-cleaning": ("ستائر", "ستارة"),
    "mattress-cleaning": ("مراتب", "مرتبة"),
    "marble-polishing": ("رخام", "جلي", "تلميع"),
    "glass-facade-cleaning": ("زجاج", "واجهات", "واجه"),
    "garage-cleaning": ("كراج", "مواقف", "سيارات"),
    "garden-cleaning": ("حدائق", "حديقة", "تنسيق"),
    "deep-cleaning": ("تنظيف", "عميق", "تعقيم"),
    "stone-facade-cleaning": ("واجه", "حجر", "تنظيف"),
    "chimney-cleaning": ("مدخنة", "مداخن"),
    "water-leak": ("تسرب", "تسريب", "مياه"),
    "gas-leak": ("غاز", "تسرب"),
    "ac-leak": ("تكييف", "تسرب", "فريون"),
    "roof-insulation": ("عزل", "سطح", "أسطح"),
    "waterproof": ("عزل", "مائي"),
    "thermal": ("عزل", "حرار"),
    "plumbing": ("سباك", "أنابيب", "مواسير"),
    "sewer": ("مجاري", "تسليك"),
    "electrical": ("كهرب", "لوحة"),
    "ac-install": ("تكييف", "مكيف"),
    "pest": ("حشرات", "مكافحة"),
    "landscap": ("حدائق", "تنسيق"),
    "swimming-pool": ("مسبح", "مسابح"),
    "paint": ("دهان", "صبغ", "طلاء", "رش"),
    "electric-spray-painting": ("رش", "دهان", "كهرب"),
    "gypsum": ("جبس", "جبسم"),
    "wooden-arbor": ("عريش", "عرائش", "خشب"),
    "wood-doors": ("دهان", "أبواب", "شبابيك"),
    "interior-design": ("تصميم", "ديكور"),
}

PLACEHOLDERS = re.compile(
    r"lorem ipsum|dummy text|your title here|نص تجريبي|اكتب هنا|coming soon|\bTODO\b|\bTBD\b|"
    r"\{PHONE|_RUKN_OMAN\}|\{\{[a-z_]+\}\}",
    re.I,
)
KAYAN_SHORTCODES = re.compile(r"\[post_[a-z_]+\]")
UAE_LEAK = re.compile(r"الإمارات|إمارة|إمارات|درهم|دبي|أبوظبي|ابوظبي|الشارقة|عجمان")
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
]
OMAN_HINT = re.compile(r"عُمان|عمان|مسقط|صلالة|نزوى|صحار|ريال")

TAG_RE = re.compile(r"<[^>]+>", re.S)
SCRIPT_RE = re.compile(r"<(script|style|noscript)[^>]*>.*?</\1>", re.I | re.S)
HEADING_RE = re.compile(r"<h([1-6])\b[^>]*>(.*?)</h\1>", re.I | re.S)
SENT_SPLIT = re.compile(r"(?<=[\.!?؟。\n])\s+")


class WP:
    def __init__(self, base: str, user: str, app_password: str):
        self.base = base.rstrip("/")
        token = base64.b64encode(f"{user}:{app_password}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {token}",
            "User-Agent": "RuknContentAudit/1.0",
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
    text = re.sub(r"\s+", " ", text).strip()
    return text


def words_of(text: str) -> list[str]:
    return re.findall(r"\S+", text)


def headings(html: str) -> list[tuple[int, str]]:
    out = []
    for m in HEADING_RE.finditer(html or ""):
        out.append((int(m.group(1)), strip_html(m.group(2))))
    return out


def split_slug(slug: str) -> tuple[str, str]:
    slug = (slug or "").strip("/")
    for city in sorted(CITIES, key=len, reverse=True):
        suffix = "-" + city
        if slug.endswith(suffix):
            return slug[: -len(suffix)], city
    return slug, ""


def service_terms(service: str) -> tuple[str, ...]:
    if service in SERVICE_TERMS:
        return SERVICE_TERMS[service]
    for key, terms in SERVICE_TERMS.items():
        if key in service or service.startswith(key):
            return terms
    # Fallback: tokenise the slug into coarse Arabic expectations.
    bits = [p for p in service.split("-") if p not in {"and", "or"}]
    extra = []
    if any(b in {"cleaning", "clean"} for b in bits):
        extra.append("تنظيف")
    if "paint" in service:
        extra.extend(["دهان", "صبغ"])
    return tuple(extra)


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
    t = re.sub(r"\s+", " ", t).strip()
    return t


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


def fetch_page(wp: WP, route: str, page: int) -> tuple[int, list, dict]:
    fields = "id,slug,link,title,content,excerpt,type,featured_media,cities,service_categories,meta"
    code, data, hdrs = wp.get(
        route,
        status="publish",
        per_page=100,
        page=page,
        context="edit",
        _fields=fields,
    )
    if code != 200 or not isinstance(data, list):
        return code, [], hdrs
    return code, data, hdrs


def fetch_all(wp: WP, route: str) -> list[dict]:
    from concurrent.futures import ThreadPoolExecutor, as_completed

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
    title = (item.get("title") or {})
    content = (item.get("content") or {})
    excerpt = (item.get("excerpt") or {})
    html = content.get("raw") or content.get("rendered") or ""
    title_txt = title.get("raw") or strip_html(title.get("rendered") or "")
    excerpt_txt = excerpt.get("raw") or strip_html(excerpt.get("rendered") or "")
    meta = item.get("meta") if isinstance(item.get("meta"), dict) else {}
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
        "h1": sum(1 for lvl, _ in heads if lvl == 1),
        "h2": sum(1 for lvl, _ in heads if lvl == 2),
        "h3": sum(1 for lvl, _ in heads if lvl == 3),
        "skeleton": skeleton,
        "skeleton_hash": hashlib.md5(skeleton.encode("utf-8")).hexdigest()[:12] if skeleton else "",
        "service": service,
        "city": city,
        "cities_tax": item.get("cities") or [],
        "cats_tax": item.get("service_categories") or [],
        "featured": int(item.get("featured_media") or 0),
        "rm_title": meta.get("rank_math_title") or "",
        "rm_desc": meta.get("rank_math_description") or "",
        "en_title": meta.get("_rukn_en_title") or "",
        "en_content": meta.get("_rukn_en_content") or "",
    }


def analyze(docs: list[dict]) -> tuple[list[dict], list[dict], dict]:
    n = max(len(docs), 1)
    sent_docs: Counter[str] = Counter()
    for d in docs:
        seen = set()
        for s in d["sentences"]:
            ns = normalize_sentence(s)
            if ns and ns not in seen:
                seen.add(ns)
                sent_docs[ns] += 1

    boiler = {s for s, c in sent_docs.items() if c >= max(3, int(n * BOILER_DOC_SHARE))}
    # Always treat known Kayan template headings as boilerplate.
    forced = [
        "علامات أن التأجيل سيكلف أكثر",
        "ماذا يتغير إذا اكتفيت بالترقيع؟",
        "حدود الحل المنزلي",
        "ما الذي لا ننصح بتجربته",
        "كيف تسير الزيارة؟",
        "هل شركة {SERVICE} مناسبة لحالتك؟",
    ]
    for s in list(sent_docs):
        if any(k in s for k in ("هل تحتاج إلى شركة", "قراءة المشكلة في بيوت", "مناسبة لحالتك", "اكتفيت بالترقيع", "التأجيل سيكلف")):
            boiler.add(s)

    fam_count = Counter(d["skeleton_hash"] for d in docs if d["skeleton_hash"])
    for d in docs:
        boiler_sents = [s for s in d["sentences"] if normalize_sentence(s) in boiler]
        boiler_words = sum(len(words_of(s)) for s in boiler_sents)
        unique_words = max(d["word_count"] - boiler_words, 0)
        ratio = (boiler_words / d["word_count"]) if d["word_count"] else 1.0
        tokens = [w.lower() for w in d["words"] if len(w) > 2]
        # Strip city tokens so city-variants collide on template body.
        city_ar = set(CITY_ALIASES)
        tokens = [t for t in tokens if t not in city_ar]
        d["simhash"] = simhash64(tokens[::2][:1200])  # stride keeps it fast
        d["boilerplate_ratio"] = round(ratio, 3)
        d["unique_word_count"] = unique_words
        d["template_family_size"] = fam_count.get(d["skeleton_hash"], 0)

    # Near-duplicate pairs via 16-bit buckets.
    buckets: dict[int, list[int]] = defaultdict(list)
    for i, d in enumerate(docs):
        buckets[d["simhash"] >> 48].append(i)
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
                pairs.append({
                    "id_a": docs[i]["id"],
                    "url_a": docs[i]["url"],
                    "title_a": docs[i]["title"],
                    "id_b": docs[j]["id"],
                    "url_b": docs[j]["url"],
                    "title_b": docs[j]["title"],
                    "hamming": dist,
                    "same_service": same_svc,
                    "kind": "city-variant-template" if same_svc and docs[i]["city"] != docs[j]["city"] else (
                        "cross-service-duplicate" if not same_svc else "near-duplicate"
                    ),
                })
    pair_index: dict[int, list[dict]] = defaultdict(list)
    for p in pairs:
        pair_index[p["id_a"]].append(p)
        pair_index[p["id_b"]].append(p)

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
        if d["unique_word_count"] < THIN_UNIQUE and d["word_count"] >= THIN_RAW:
            issues.append("thin_unique")
            notes.append(
                f"الكلمات الفريدة بعد حذف القوالب {d['unique_word_count']} (نسبة القالب {d['boilerplate_ratio']:.0%})."
            )
        if d["boilerplate_ratio"] >= 0.35 or (
            d["template_family_size"] >= TEMPLATE_FAMILY_MIN
            and d["skeleton"]
            and d["word_count"] >= 400
        ):
            issues.append("template_boilerplate")
            notes.append(
                f"هيكل H2 مكرر على {d['template_family_size']} مقالة، ونسبة الجمل المكررة {d['boilerplate_ratio']:.0%}."
            )

        related = pair_index.get(d["id"], [])
        if related:
            best = min(related, key=lambda p: p["hamming"])
            other = best["url_b"] if best["id_a"] == d["id"] else best["url_a"]
            issues.append("duplicate_similar")
            notes.append(
                f"تشابه مرتفع (hamming={best['hamming']}, {best['kind']}) مع {other}."
            )
            d["similar_to"] = other
            d["similarity_kind"] = best["kind"]
            d["hamming"] = best["hamming"]
        else:
            d["similar_to"] = ""
            d["similarity_kind"] = ""
            d["hamming"] = ""

        # Intent / relevance
        slug_city = d["city"]
        title_city = city_from_title(title)
        if slug_city and title_city and slug_city != title_city:
            issues.append("intent_mismatch")
            notes.append(f"المدينة في العنوان ({title_city}) تختلف عن الـ slug ({slug_city}).")
        if slug_city:
            ar = CITIES[slug_city]
            others = {k: v for k, v in CITIES.items() if k != slug_city}
            own = text.count(ar)
            rival = max(((text.count(v), k) for k, v in others.items()), default=(0, ""))
            if own == 0 and d["type"] == "post":
                issues.append("intent_mismatch")
                notes.append(f"المحتوى لا يذكر مدينة الـ slug «{ar}».")
            elif rival[0] >= own + 3 and rival[0] >= 4:
                issues.append("intent_mismatch")
                notes.append(f"المحتوى يكرر «{CITIES[rival[1]]}» ({rival[0]}) أكثر من «{ar}» ({own}).")
        terms = service_terms(d["service"]) if d["type"] == "post" else ()
        if terms:
            hits = [t for t in terms if t in text or t in title]
            if len(hits) < max(1, len(terms) // 2) and d["word_count"] > 80:
                issues.append("intent_mismatch")
                notes.append(f"كلمات الخدمة المتوقعة ناقصة: {', '.join(terms)} (وُجد: {', '.join(hits) or 'لا شيء'}).")
        if d["type"] == "post" and title and text:
            title_tokens = [w for w in re.findall(r"[\u0600-\u06FFa-zA-Z]{3,}", title)]
            overlap = sum(1 for w in title_tokens if w in text)
            if title_tokens and overlap / len(title_tokens) < 0.35:
                issues.append("intent_mismatch")
                notes.append("جسم المقال لا يعيد أغلب كلمات العنوان (ضعف ارتباط النية).")
        if d["en_title"] and re.search(r"[\u0600-\u06FF]", d["en_title"]):
            issues.append("intent_mismatch")
            notes.append("العنوان الإنجليزي ما زال يحتوي حروفاً عربية.")

        # Errors / missing SEO
        shorts = sorted(set(KAYAN_SHORTCODES.findall(html)))
        if shorts:
            issues.append("unexpanded_shortcodes")
            notes.append("شورت كود كيان غير مُفسَّر (أقسام ناقصة في HTML): " + ", ".join(shorts[:6]) + ".")
        if d["h1"] > 1:
            issues.append("structural_error")
            notes.append(f"أكثر من H1 داخل المحتوى ({d['h1']}).")
        if d["h2"] == 0 and d["word_count"] > 250 and d["slug"] not in {"html-sitemap", "en-home"}:
            issues.append("missing_headings")
            notes.append("لا توجد عناوين H2 رغم طول النص.")
        ph = PLACEHOLDERS.findall(html)
        if ph:
            issues.append("placeholder")
            notes.append("عناصر نائبة: " + ", ".join(sorted(set(ph))[:6]))
        uae = UAE_LEAK.findall(text + title)
        if uae and not re.search(r"مقارنة|وليس", text):
            issues.append("structural_error")
            notes.append("كلمات إماراتية متبقية: " + ", ".join(sorted(set(uae))[:5]))
        if re.search(r'''href=["']tel:''', html):
            issues.append("tel_in_content")
            notes.append("ما زال هناك رابط اتصال هاتفي tel: داخل المحتوى.")
        if d["type"] == "post" and not d["rm_desc"]:
            issues.append("missing_meta")
            notes.append("وصف Rank Math فارغ.")
        if d["type"] == "post" and not d["cities_tax"]:
            issues.append("missing_meta")
            notes.append("المقالة غير مربوطة بتصنيف المدن.")
        if d["type"] == "post" and not d["cats_tax"]:
            issues.append("missing_meta")
            notes.append("المقالة غير مربوطة بتصنيف الخدمات.")
        if d["featured"] in (0, 246) and d["type"] == "post":
            issues.append("missing_meta")
            notes.append(f"صورة بارزة مفقودة أو مكررة (id={d['featured']}).")
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
        issues = issue_set

        cats = []
        for flag, label in (
            ("thin_raw", "Thin Content"),
            ("thin_unique", "Thin Content"),
            ("template_boilerplate", "Template/Boilerplate"),
            ("duplicate_similar", "Duplicate/Similar"),
            ("intent_mismatch", "Intent Mismatch"),
            ("unexpanded_shortcodes", "Missing SEO Elements"),
            ("missing_headings", "Missing SEO Elements"),
            ("missing_meta", "Missing SEO Elements"),
            ("placeholder", "Errors/Placeholders"),
            ("structural_error", "Errors/Placeholders"),
            ("tel_in_content", "Errors/Placeholders"),
        ):
            if flag in issues and label not in cats:
                cats.append(label)

        primary = cats[0] if cats else "OK"

        rows.append({
            "id": d["id"],
            "type": d["type"],
            "title": d["title"],
            "url": d["url"],
            "slug": d["slug"],
            "service": d["service"],
            "city": d["city"],
            "word_count": d["word_count"],
            "unique_word_count": d["unique_word_count"],
            "boilerplate_ratio": d["boilerplate_ratio"],
            "h1": d["h1"],
            "h2": d["h2"],
            "h3": d["h3"],
            "template_family_size": d["template_family_size"],
            "similar_to": d["similar_to"],
            "similarity_kind": d["similarity_kind"],
            "hamming": d["hamming"],
            "issue_flags": "|".join(issues),
            "issue_categories": " | ".join(cats) if cats else "OK",
            "primary_issue": primary,
            "observations": " ".join(notes) if notes else "No major content issues detected.",
        })

    stats = {
        "docs": n,
        "boiler_sentences": len(boiler),
        "pairs": len(pairs),
        "forced": forced,
        "fam_count": fam_count,
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
            if key in {"title", "observations", "url", "similar_to"} and len(val) > 120:
                val = val[:117] + "..."
            vals.append(val)
        lines.append("| " + " | ".join(vals) + " |")
    extra = len(rows) - limit
    if extra > 0:
        lines.append(f"\n_{extra} additional rows in the CSV._")
    return "\n".join(lines) + "\n"


def write_markdown(path: Path, rows: list[dict], pairs: list[dict], stats: dict) -> None:
    flagged = [r for r in rows if r["issue_categories"] != "OK"]
    thin = [r for r in rows if "Thin Content" in r["issue_categories"]]
    templ = [r for r in rows if "Template/Boilerplate" in r["issue_categories"]]
    dup = [r for r in rows if "Duplicate/Similar" in r["issue_categories"]]
    intent = [r for r in rows if "Intent Mismatch" in r["issue_categories"]]
    missing = [r for r in rows if "Missing SEO Elements" in r["issue_categories"]]
    errors = [r for r in rows if "Errors/Placeholders" in r["issue_categories"]]
    ok = [r for r in rows if r["issue_categories"] == "OK"]
    wc = sorted(r["word_count"] for r in rows)
    median = wc[len(wc) // 2] if wc else 0
    fams = [(h, c) for h, c in stats["fam_count"].most_common(8) if h]

    sitewide = []
    n = max(len(rows), 1)
    flag_n = Counter()
    for r in rows:
        for f in (r.get("issue_flags") or "").split("|"):
            if f:
                flag_n[f] += 1
    if flag_n.get("unexpanded_shortcodes", 0) / n >= 0.8:
        sitewide.append(
            f"**Unexpanded Kayan shortcodes** on {flag_n['unexpanded_shortcodes']} URLs "
            "(`[post_features]`, `[post_steps]`, `[post_prices]`, `[post_services]`, `[post_call]`). "
            "Those blocks never become unique HTML for Googlebot."
        )
    if flag_n.get("tel_in_content", 0) / n >= 0.8:
        sitewide.append(
            f"**`tel:` call links remain in raw HTML** on {flag_n['tel_in_content']} posts "
            "(the live theme hides them with CSS; source still contains the CTA)."
        )
    if flag_n.get("template_boilerplate", 0) / n >= 0.5:
        sitewide.append(
            f"**Shared Kayan article template** on {flag_n['template_boilerplate']} URLs "
            "(boilerplate ratio typically 35–53% after city names are stripped)."
        )

    def top(rows_in, key="word_count", reverse=False, n=25):
        return sorted(rows_in, key=lambda r: (r.get(key) or 0), reverse=reverse)[:n]

    cols_main = [
        ("title", "Title"),
        ("url", "URL"),
        ("word_count", "Words"),
        ("unique_word_count", "Unique words"),
        ("issue_categories", "Issue category"),
        ("observations", "Observations"),
    ]

    md = []
    md.append("# Oman content & on-page SEO audit")
    md.append("")
    md.append("Source: live published REST content on `https://rukn-eltatawer.com/om` (posts + pages + services).")
    md.append(f"Generated by `scripts/content_seo_audit.py`. Documents analysed: **{stats['docs']}**.")
    md.append("")
    md.append("## Executive summary")
    md.append("")
    md.append("| Metric | Value |")
    md.append("| --- | --- |")
    md.append(f"| Published URLs scanned | {stats['docs']} |")
    md.append(f"| Median word count | {median} |")
    md.append(f"| URLs with at least one issue | {len(flagged)} |")
    md.append(f"| Clean (no flags) | {len(ok)} |")
    md.append(f"| Thin (<{THIN_RAW} raw words, or <{THIN_UNIQUE} unique after boilerplate) | {len(thin)} |")
    md.append(f"| Template / boilerplate | {len(templ)} |")
    md.append(f"| Duplicate / similar | {len(dup)} |")
    md.append(f"| Intent / relevance mismatch | {len(intent)} |")
    md.append(f"| Missing SEO elements | {len(missing)} |")
    md.append(f"| Errors / placeholders | {len(errors)} |")
    md.append(f"| Near-duplicate pairs | {stats['pairs']} |")
    md.append("")
    md.append("### Sitewide findings (not unique to one URL)")
    md.append("")
    for item in sitewide:
        md.append(f"- {item}")
    md.append("")
    md.append("The CSV still records these flags on every matching URL. Tables below highlight **URL-specific** risk: thin hubs, city-variant clones, and cross-service cannibalisation.")
    md.append("")
    md.append("### How scores are calculated")
    md.append("")
    md.append("- **Raw words**: whitespace tokens after scripts/styles/HTML are stripped.")
    md.append(f"- **Thin (raw)**: fewer than {THIN_RAW} tokens — Google’s helpful-content bar for commercial service pages.")
    md.append(f"- **Unique words**: raw words minus sentences that appear in ≥{int(BOILER_DOC_SHARE*100)}% of the corpus (Kayan template padding).")
    md.append("- **Template family**: identical H2 skeleton after city/service names are normalised.")
    md.append("- **Similarity**: 64-bit simhash on de-citied body tokens; Hamming ≤ 8 ≈ near-duplicate.")
    md.append("- **H1**: Kayan renders the post title as H1 in the theme. Body HTML without `<h1>` is expected and is **not** flagged.")
    md.append("- Unexpanded `[post_features]` / `[post_steps]` shortcodes mean those Kayan blocks never reach Googlebot as unique copy.")
    md.append("")
    md.append("Most local-service URLs are **city variants of one Kayan article template**. Raw length is often 2,000+ words, but uniqueness is low. That is the core SEO risk: keyword cannibalisation across eight cities and weak distinctive value per URL.")
    md.append("")
    md.append("## 1. Thin content")
    md.append("")
    md.append(md_table(top(thin, "word_count", False, 40), cols_main, 40))
    md.append("## 2. Template & boilerplate overuse")
    md.append("")
    md.append("Largest shared heading skeletons:")
    md.append("")
    md.append("| Family hash | Articles |")
    md.append("| --- | --- |")
    for h, c in fams:
        md.append(f"| `{h}` | {c} |")
    md.append("")
    md.append(md_table(top(templ, "boilerplate_ratio", True, 30), cols_main, 30))
    md.append("## 3. Duplicate / similar content")
    md.append("")
    md.append(f"Near-duplicate pairs: **{len(pairs)}**. City-variant pairs are expected from the generator; cross-service pairs are cannibalisation.")
    md.append("")
    pair_cols = [
        ("kind", "Kind"),
        ("hamming", "Hamming"),
        ("title_a", "Title A"),
        ("url_a", "URL A"),
        ("title_b", "Title B"),
        ("url_b", "URL B"),
    ]
    cross = [p for p in pairs if p["kind"] == "cross-service-duplicate"]
    cityv = [p for p in pairs if p["kind"] == "city-variant-template"]
    md.append("### Cross-service duplicates (highest risk)")
    md.append("")
    md.append(md_table(sorted(cross, key=lambda p: p["hamming"])[:40], pair_cols, 40))
    md.append("### City-variant templates (same service, different city)")
    md.append("")
    md.append(md_table(sorted(cityv, key=lambda p: p["hamming"])[:25], pair_cols, 25))
    md.append("## 4. Search intent & relevance mismatch")
    md.append("")
    md.append(md_table(intent[:40], cols_main, 40))
    md.append("## 5. Errors & missing SEO elements")
    md.append("")
    miss_err = missing + [r for r in errors if r not in missing]
    # de-dup by id
    seen = set()
    combined = []
    for r in missing + errors:
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        combined.append(r)
    md.append(md_table(combined[:50], cols_main, 50))
    md.append("## Recommendations")
    md.append("")
    md.append("1. **Service CPT hubs** (`/services/{slug}/`): replace the 43-word stubs with unique 1,000+ word category guides that link down to city articles.")
    md.append("2. **City variants**: keep the URL map, but rewrite the first 300 words, FAQs, and proof (areas, climate, access) so eight cities are not the same article with a city token swapped.")
    md.append("3. **Expand or delete `[post_*]` shortcodes** so features/steps/prices exist as HTML, not leftover tokens.")
    md.append("4. **Remove `tel:` from post HTML** (hiding with CSS does not remove the node from the DOM or from some crawlers).")
    md.append("5. **Merge overlapping intents** (e.g. central AC vs duct maintenance in the same city) where Hamming ≤ 4.")
    md.append("6. **Utility pages** (FAQ, cities, contact, about): they can stay short, but add unique copy and do not compete with commercial articles.")
    md.append("")
    md.append("")
    md.append("Every published URL is in `docs/content-seo-audit.csv`. Pairwise near-duplicates are in `docs/content-seo-audit-pairs.csv`.")
    md.append("")
    path.write_text("\n".join(md), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default=os.environ.get("WP_BASE", DEFAULT_BASE))
    parser.add_argument("--out-dir", default=str(ROOT / "docs"))
    parser.add_argument("--cache", default="/tmp/rukn-content-audit-cache.json")
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
            raise SystemExit("Set WP_USER and WP_APP_PASSWORD (or pass --cache)")
        wp = WP(args.base, user, app)
        code, me, _ = wp.get("/wp/v2/users/me", context="edit")
        if code != 200 or not isinstance(me, dict):
            raise SystemExit(f"auth failed {code}: {me}")
        print("auth", me.get("slug"), me.get("roles"), flush=True)
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
    print("unpacked", len(docs), "median words", sorted(d["word_count"] for d in docs)[len(docs)//2] if docs else 0, flush=True)
    rows, pairs, stats = analyze(docs)
    out = Path(args.out_dir)
    write_csv(
        out / "content-seo-audit.csv",
        rows,
        [
            "id", "type", "title", "url", "slug", "service", "city",
            "word_count", "unique_word_count", "boilerplate_ratio",
            "h1", "h2", "h3", "template_family_size",
            "similar_to", "similarity_kind", "hamming",
            "issue_flags", "issue_categories", "primary_issue", "observations",
        ],
    )
    write_csv(
        out / "content-seo-audit-pairs.csv",
        sorted(pairs, key=lambda p: (p["kind"], p["hamming"])),
        ["kind", "hamming", "id_a", "title_a", "url_a", "id_b", "title_b", "url_b", "same_service"],
    )
    write_markdown(out / "content-seo-audit.md", rows, pairs, stats)
    print("wrote", out / "content-seo-audit.csv", flush=True)
    print("wrote", out / "content-seo-audit.md", flush=True)
    print("flagged", sum(1 for r in rows if r["issue_categories"] != "OK"), "/", len(rows), flush=True)


if __name__ == "__main__":
    main()
