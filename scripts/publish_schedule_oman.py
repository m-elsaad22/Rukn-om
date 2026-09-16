#!/usr/bin/env python3
"""Finish WP/theme/Rank Math setup, publish the top draft, schedule the rest every 10 minutes.

Credentials from the environment (never committed):
  WP_USER, WP_APP_PASSWORD, WP_ADMIN_PASSWORD, WP_BASE
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from oman_copy import (  # noqa: E402
    CITIES,
    SERVICES,
    unique_ar_section,
    unique_en_article,
    unique_intro_ar,
)
from seo_fix_oman import WP, Admin, strip_uae  # noqa: E402

PHONE = os.environ.get("WP_PHONE", "+971586634710")
WHATSAPP = os.environ.get("WP_WHATSAPP", "971586634710")
MUSCAT = timezone(timedelta(hours=4))

# Search-demand priority for Oman (lower index = publish sooner).
PRIORITY = [
    "water-leak-detection",
    "water-pipe-leak-detection",
    "ac-leak-detection",
    "gas-leak-detection",
    "split-ac-maintenance",
    "central-ac-maintenance",
    "split-ac-installation",
    "ac-cleaning-washing",
    "ac-freon-refill",
    "ac-duct-maintenance",
    "ac-relocation-installation",
    "window-ac-installation",
    "new-central-ac-installation",
    "cooling-fault-detection",
    "commercial-refrigeration-maintenance",
    "ac-periodic-maintenance-contracts",
    "ac-tech",
    "plumbing-fault-repair",
    "home-plumber",
    "home-plumber-elec",
    "drain-unclogging",
    "drainage-pipe-maintenance",
    "septic-tank-emptying",
    "water-heater-installation",
    "water-heater-maintenance",
    "water-pump-maintenance",
    "water-pumps",
    "plumbing-maintenance",
    "sanitary-fixtures-installation",
    "roof-insulation",
    "waterproofing",
    "thermal-insulation",
    "humidity-treatment",
    "bathroom-insulation",
    "kitchen-insulation",
    "tank-insulation",
    "tank-lining-maintenance",
    "soundproofing",
    "24h-emergency-electrician",
    "electrical-fault-detection",
    "electrical-maintenance",
    "home-electrician",
    "home-electrician-elec",
    "electric-panel-maintenance",
    "new-electrical-wiring",
    "general-maintenance",
    "building-maintenance",
    "deep-cleaning",
    "home-cleaning",
    "apartment-cleaning",
    "villa-cleaning",
    "office-cleaning",
    "water-tank-cleaning",
    "bathroom-cleaning",
    "kitchen-cleaning",
    "carpet-cleaning",
    "glass-facade-cleaning",
    "duct-cleaning",
    "chimney-cleaning",
    "stone-facade-cleaning",
    "garage-cleaning",
    "cockroach-control",
    "termite-control",
    "bed-bug-control",
    "rodent-control",
    "ant-control",
    "mosquito-fly-control",
    "crawling-pest-control",
    "flying-pest-control",
    "bathroom-renovation",
    "kitchen-renovation",
    "old-house-renovation",
    "building-renovation",
    "villa-inspection",
    "crack-repair",
    "villa-painting",
    "apartment-painting",
    "interior-painting",
    "exterior-painting",
    "exterior-facade-painting",
    "solar-ac-installation",
    "solar-water-heaters",
    "solar-systems-installation",
    "cctv-tech",
    "cctv-maintenance",
    "water-filters",
    "ro-plants",
]

CITY_RANK = {slug: i for i, slug in enumerate(["muscat", "salalah", "sohar", "nizwa", "sur", "rustaq", "ibri", "al-buraimi"])}
PRIO_RANK = {slug: i for i, slug in enumerate(PRIORITY)}


def split_slug(slug: str) -> tuple[str, str]:
    for city in sorted(CITIES, key=len, reverse=True):
        if slug.endswith("-" + city):
            return slug[: -(len(city) + 1)], city
    return slug, "muscat"


def score(slug: str) -> tuple[int, int, str]:
    service, city = split_slug(slug)
    return (PRIO_RANK.get(service, 500), CITY_RANK.get(city, 50), slug)


def unique_en_meta(title: str, slug: str) -> tuple[str, str, str]:
    service, city = split_slug(slug)
    if service in SERVICES and city in CITIES:
        art = unique_en_article(service, city, title)
        return art["title"], art["html"], art["desc"]
    c = CITIES.get(city, CITIES["muscat"])
    svc_en = service.replace("-", " ").title()
    en_title = f"{svc_en} in {c['en']}, Oman"
    html = (
        f"<section><h2>{en_title}</h2>"
        f"<p>Rukn Eltatawer provides {svc_en.lower()} in {c['en']}, {c['gov_en']}. "
        f"{c['note_en']}. Local conditions: {c['climate_en']}. Building stock: {c['stock_en']}.</p>"
        f"<p>Neighbourhoods we cover: {c['areas_en']}. Pricing is in Omani rial after an on-site visit.</p>"
        f'<p>Arabic page: <a href="/om/{slug}/">{title}</a>.</p></section>'
    )
    desc = (
        f"{svc_en} in {c['en']} ({c['gov_en']}): {c['climate_en']}. "
        f"On-site survey and a written quote in OMR."
    )[:160]
    return en_title, html, desc


def seo_meta(title: str, slug: str, seo_title: str, desc: str) -> dict:
    service, city = split_slug(slug)
    en_title, en_html, en_desc = unique_en_meta(title, slug)
    focus = f"{title} {CITIES.get(city, CITIES['muscat'])['ar']}"
    canon = f"https://rukn-eltatawer.com/om/{slug}/"
    return {
        "rank_math_title": seo_title,
        "rank_math_description": desc,
        "rank_math_focus_keyword": focus[:80],
        "rank_math_canonical_url": canon,
        "rank_math_robots": "index, follow",
        "rank_math_facebook_title": seo_title,
        "rank_math_facebook_description": desc,
        "rank_math_twitter_title": seo_title,
        "rank_math_twitter_description": desc,
        "_rukn_lang": "ar",
        "_rukn_pair_slug": slug,
        "_rukn_en_title": en_title,
        "_rukn_en_content": en_html,
        "_rukn_en_desc": en_desc,
        "_rukn_en_excerpt": en_desc,
    }


def prepare_content(raw: str, title: str, slug: str) -> tuple[str, str, str]:
    service, city = split_slug(slug)
    html = strip_uae(raw or "")
    html = html.replace("{PHONE_RUKN_OMAN}", PHONE)
    html = html.replace("{WHATSAPP_RUKN_OMAN}", WHATSAPP)
    html = re.sub(r"<h1(\b[^>]*)>", r"<h2\1>", html, count=1, flags=re.I)
    html = re.sub(r"</h1>", "</h2>", html, count=1, flags=re.I)
    html = re.sub(r"<!--rukn-local-start-->.*?<!--rukn-local-end-->", "", html, flags=re.S)
    city_info = CITIES.get(city, CITIES["muscat"])
    if service in SERVICES and city in CITIES:
        if "rukn-oman-intro" not in html:
            html = unique_intro_ar(service, city).replace("<p>", '<p class="rukn-oman-intro">', 1) + html
        section = unique_ar_section(service, city)
    else:
        section = f"""<!--rukn-local-start-->
<section class="rukn-oman-local">
<h2>{title} في {city_info["ar"]} — {city_info["gov_ar"]}</h2>
<p>ركن التطور ينفّذ هذه الخدمة {city_info["prep"]} داخل {city_info["gov_ar"]}. {city_info["note_ar"]}. طبيعة المكان: {city_info["climate_ar"]}. المباني الشائعة: {city_info["stock_ar"]}.</p>
<p>التغطية الميدانية: {city_info["areas_ar"]}. المعاينة قبل أي سعر، والتسعير بالريال العُماني وليس بعملة دولة أخرى.</p>
</section>
<!--rukn-local-end-->"""
    idx = html.rfind("</section>")
    html = html[:idx] + section + html[idx:] if idx != -1 else html + section
    desc = (
        f"{title} في {city_info['ar']} داخل {city_info['gov_ar']}. "
        f"معاينة ميدانية وسعر بالريال العُماني. تغطية: {city_info['areas_ar'][:60]}."
    )[:160]
    seo_title = f"{title} | ركن التطور عُمان"
    return html, seo_title, desc


def list_drafts(wp: WP) -> list[dict]:
    items = []
    page = 1
    while True:
        code, data, hdrs = wp.get(
            "/wp/v2/posts",
            status="draft",
            per_page=100,
            page=page,
            context="edit",
            _fields="id,slug,title,featured_media",
        )
        if code != 200 or not isinstance(data, list) or not data:
            break
        items.extend(data)
        pages = int(hdrs.get("X-WP-TotalPages") or hdrs.get("x-wp-totalpages") or 1)
        if page >= pages:
            break
        page += 1
    return items


def cover_id(wp: WP) -> int:
    code, data, _ = wp.get("/wp/v2/posts", slug="home-cleaning-muscat", per_page=1, context="edit")
    if code == 200 and data:
        mid = int(data[0].get("featured_media") or 0)
        if mid:
            return mid
    code, media, _ = wp.get("/wp/v2/media", per_page=1)
    if code == 200 and media:
        return int(media[0]["id"])
    return 0


RANKMATH_SNIPPET = r"""
if (!function_exists('rukn_rankmath_oman_setup')) {
    function rukn_rankmath_oman_setup() {
        add_filter('rank_math/registration/skip', '__return_true');
        if (get_option('rukn_rankmath_setup') === '1.1') {
            return;
        }
        update_option('rank_math_wizard_completed', true);
        if (!get_option('rank_math_connect_data')) {
            update_option('rank_math_connect_data', array(
                'username' => 'rukn-oman',
                'email' => 'admin@rukn-eltatawer.com',
            ));
        }
        add_filter('rank_math/registration/skip', '__return_true', 1);
        $titles = get_option('rank-math-options-titles', array());
        if (!is_array($titles)) { $titles = array(); }
        $titles['homepage_title'] = 'ركن التطور عُمان | تنظيف وصيانة وكشف تسربات في مسقط وصلالة وكل مدن السلطنة';
        $titles['homepage_description'] = 'شركة خدمات منزلية في سلطنة عُمان: تنظيف، كشف تسربات، عزل، صيانة وتكييف. عرض سعر بالريال العُماني بعد المعاينة.';
        $titles['pt_post_title'] = '%title% %sep% ركن التطور عُمان';
        $titles['pt_post_description'] = '%excerpt%';
        $titles['pt_page_title'] = '%title% %sep% ركن التطور عُمان';
        $titles['title_separator'] = '-';
        $titles['disable_author_archives'] = 'on';
        $titles['disable_date_archives'] = 'on';
        $titles['noindex_empty_taxonomies'] = 'on';
        $titles['noindex_search'] = 'on';
        update_option('rank-math-options-titles', $titles);
        $sm = get_option('rank-math-options-sitemap', array());
        if (!is_array($sm)) { $sm = array(); }
        $sm['pt_post_sitemap'] = 'on';
        $sm['pt_page_sitemap'] = 'on';
        $sm['authors_sitemap'] = 'off';
        update_option('rank-math-options-sitemap', $sm);
        $gen = get_option('rank-math-options-general', array());
        if (!is_array($gen)) { $gen = array(); }
        $gen['attachment_redirect_urls'] = 'on';
        $gen['new_window_external_links'] = 'on';
        update_option('rank-math-options-general', $gen);
        update_option('rukn_rankmath_setup', '1.1');
    }
    add_action('plugins_loaded', 'rukn_rankmath_oman_setup', 20);
    if (did_action('plugins_loaded')) { rukn_rankmath_oman_setup(); }
}
""".strip()


def upsert_snippet(wp: WP) -> None:
    code, data, _ = wp.get("/code-snippets/v1/snippets", per_page=50)
    found = None
    if code == 200 and isinstance(data, list):
        for item in data:
            if item.get("name") == "Rukn Rank Math Oman setup":
                found = item
                break
    payload = {
        "name": "Rukn Rank Math Oman setup",
        "desc": "Skip Rank Math wizard and set Oman titles/sitemap options",
        "code": RANKMATH_SNIPPET,
        "scope": "global",
        "active": True,
        "priority": 5,
    }
    if found:
        code, data, _ = wp.request("PUT", f"/code-snippets/v1/snippets/{found['id']}", data=payload)
        print("rankmath snippet update", code, data.get("active") if isinstance(data, dict) else data)
    else:
        code, data, _ = wp.post("/code-snippets/v1/snippets", payload)
        print("rankmath snippet create", code, data.get("id") if isinstance(data, dict) else data)


def fix_theme_schema(admin: Admin) -> None:
    url = admin.base + "/wp-admin/admin.php?page=yts-schema"
    code, body, _, _ = admin.open(url)
    html = body.decode("utf-8", "replace")
    fields = {}
    for m in re.finditer(r"<input([^>]+)>", html, re.I):
        tag = m.group(1)
        name_m = re.search(r'name="([^"]+)"', tag)
        val_m = re.search(r'value="([^"]*)"', tag)
        typ_m = re.search(r'type="([^"]+)"', tag)
        if not name_m:
            continue
        name = name_m.group(1)
        typ = (typ_m.group(1) if typ_m else "text").lower()
        if typ in {"checkbox", "radio"} and "checked" not in tag.lower():
            continue
        fields[name] = val_m.group(1) if val_m else "on"
    updates = {
        "sitename__schema": "ركن التطور عُمان",
        "YourColor_Schema_business[Business_Name]": "ركن التطور عُمان",
        "YourColor_Schema_business[Street_Address]": "مسقط، سلطنة عُمان",
        "YourColor_Schema_business[Country]": "OM",
        "YourColor_Schema_business[City]": "مسقط",
        "YourColor_Schema_business[State]": "محافظة مسقط",
        "YourColor_Schema_business[telephone]": PHONE,
        "YourColor_Schema_business[Price_Range]": "OMR",
        "YourColor_Schema_business[openingHours]": "Sa-Th 08:00-21:00",
        "YourColor_Schema_business[Service_Offered_Name]": "تنظيف، كشف تسربات، عزل، صيانة، سباكة، تكييف",
        "YourColor_Service[addressLocality]": "مسقط",
        "YourColor_Service[telephone]": PHONE,
        "YourColor_Service[addressCountry]": "OM",
        "YourColor_Service[addressRegion]": "سلطنة عُمان",
    }
    # Unhide LocalBusiness schema.
    fields.pop("YourColor_Schema_business[hide_schema_business]", None)
    fields.pop("hide_schema_business", None)
    fields.update(updates)
    nonce = re.search(r'name="_wpnonce" value="([^"]+)"', html)
    if nonce:
        fields["_wpnonce"] = nonce.group(1)
    payload = urllib_encode(fields)
    code, body, _, final = admin.open(
        url,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    print("theme schema save", code, final[-40:])


def urllib_encode(fields: dict) -> bytes:
    import urllib.parse

    return urllib.parse.urlencode(fields, doseq=True).encode()


def publish_privacy(wp: WP) -> None:
    code, data, _ = wp.get("/wp/v2/pages", slug="privacy-policy", status="any", context="edit")
    html = """
<p>توضح هذه الصفحة كيف يتعامل موقع ركن التطور عُمان مع بيانات التواصل التي تصلنا عبر النموذج أو واتساب أو الاتصال.</p>
<h2>ما نجمعه</h2>
<p>الاسم، رقم الهاتف، المدينة، ووصف الخدمة المطلوبة لتنسيق المعاينة وتقديم عرض سعر بالريال العُماني.</p>
<h2>كيف نستخدمها</h2>
<p>للتواصل بشأن طلبك فقط. لا نبيع بيانات العملاء ولا نرسلها لجهات تسويق خارج سلطنة عُمان.</p>
<h2>الاحتفاظ</h2>
<p>نحتفظ ببيانات الطلب أثناء تنفيذ الخدمة والمتابعة، ثم نحذف ما لم يعد لازماً للضمان أو المحاسبة.</p>
<h2>التواصل</h2>
<p>للاستفسار عن البيانات: واتساب أو اتصال على الرقم الظاهر في الموقع.</p>
""".strip()
    payload = {
        "title": "سياسة الخصوصية",
        "status": "publish",
        "content": html,
        "slug": "privacy-policy",
        "excerpt": "كيف يتعامل ركن التطور عُمان مع بيانات طلبات الخدمة في سلطنة عُمان.",
    }
    if code == 200 and data:
        pid = data[0]["id"]
        code, out, _ = wp.post(f"/wp/v2/pages/{pid}", payload)
        print("privacy update", code, out.get("link"))
    else:
        code, out, _ = wp.post("/wp/v2/pages", payload)
        print("privacy create", code, out.get("link") if isinstance(out, dict) else out)


def list_future(wp: WP) -> list[dict]:
    items = []
    page = 1
    while True:
        code, data, hdrs = wp.get(
            "/wp/v2/posts",
            status="future",
            per_page=100,
            page=page,
            context="edit",
            _fields="id,slug,title,date",
        )
        if code != 200 or not isinstance(data, list) or not data:
            break
        items.extend(data)
        pages = int(hdrs.get("X-WP-TotalPages") or hdrs.get("x-wp-totalpages") or 1)
        if page >= pages:
            break
        page += 1
    return items


def post_retry(wp: WP, route: str, payload: dict, attempts: int = 4):
    last = (599, {}, {})
    for i in range(attempts):
        last = wp.post(route, payload)
        if last[0] in (200, 201):
            return last
        time.sleep(1.2 * i + 0.6)
    return last


def get_retry(wp: WP, route: str, attempts: int = 4, **query):
    last = (599, {}, {})
    for i in range(attempts):
        last = wp.get(route, **query)
        if last[0] == 200:
            return last
        time.sleep(1.2 * i + 0.4)
    return last


def next_slot(now: datetime | None = None, minutes: int = 10) -> datetime:
    now = now or datetime.now(MUSCAT)
    now = now.replace(second=0, microsecond=0)
    rem = now.minute % minutes
    if rem:
        now = now + timedelta(minutes=(minutes - rem))
    else:
        now = now + timedelta(minutes=minutes)
    return now


def schedule_drafts(wp: WP, publish_first: bool = True, interval_minutes: int = 10) -> None:
    drafts = list_drafts(wp)
    print("drafts", len(drafts), "interval", interval_minutes, "min", flush=True)
    drafts.sort(key=lambda d: score(d.get("slug") or ""))
    media = cover_id(wp)
    start = next_slot(minutes=interval_minutes)
    published = scheduled = failed = 0
    first = publish_first
    step = 0
    for post in drafts:
        slug = post.get("slug") or ""
        title = (post.get("title") or {}).get("raw") or (post.get("title") or {}).get("rendered") or slug
        code_c, full, _ = get_retry(wp, f"/wp/v2/posts/{post['id']}", context="edit", _fields="id,content,title,featured_media")
        raw = ""
        feat = post.get("featured_media") or 0
        if code_c == 200 and isinstance(full, dict):
            raw = (full.get("content") or {}).get("raw") or ""
            title = (full.get("title") or {}).get("raw") or title
            feat = full.get("featured_media") or feat
        html, seo_title, desc = prepare_content(raw, title, slug)
        payload = {
            "content": html,
            "excerpt": desc,
            "featured_media": feat or media or 0,
            "meta": seo_meta(title, slug, seo_title, desc),
        }
        if first:
            payload["status"] = "publish"
            payload["date"] = datetime.now(MUSCAT).strftime("%Y-%m-%dT%H:%M:%S")
        else:
            when = start + timedelta(minutes=interval_minutes * step)
            payload["status"] = "future"
            payload["date"] = when.strftime("%Y-%m-%dT%H:%M:%S")
            step += 1
        code, data, _ = post_retry(wp, f"/wp/v2/posts/{post['id']}", payload)
        if code in (200, 201):
            if first:
                published += 1
                print("PUBLISH NOW", slug, data.get("link"), data.get("status"), flush=True)
                first = False
            else:
                scheduled += 1
                if scheduled <= 5 or scheduled % 50 == 0:
                    print(f"SCHEDULE {scheduled} {payload['date']} {slug} {data.get('status')}", flush=True)
        else:
            failed += 1
            print("FAIL", slug, code, data, flush=True)
        time.sleep(0.04)
    print(json.dumps({"published_now": published, "scheduled": scheduled, "failed": failed, "total": len(drafts), "first_slot": start.isoformat()}, ensure_ascii=False), flush=True)


def list_published(wp: WP) -> list[dict]:
    items = []
    page = 1
    while True:
        code, data, hdrs = wp.get(
            "/wp/v2/posts",
            status="publish",
            per_page=100,
            page=page,
            context="edit",
            _fields="id,slug,date",
        )
        if code != 200 or not isinstance(data, list) or not data:
            break
        items.extend(data)
        pages = int(hdrs.get("X-WP-TotalPages") or hdrs.get("x-wp-totalpages") or 1)
        if page >= pages:
            break
        page += 1
    return items


def last_published_dt(wp: WP) -> datetime | None:
    code, data, _ = wp.get(
        "/wp/v2/posts",
        status="publish",
        per_page=1,
        orderby="date",
        order="desc",
        context="edit",
        _fields="id,slug,date",
    )
    if code != 200 or not data:
        return None
    raw = data[0].get("date") or ""
    try:
        return datetime.fromisoformat(raw).replace(tzinfo=MUSCAT)
    except ValueError:
        return None


def backdate_window(wp: WP, start: datetime, end: datetime) -> None:
    """Spread remaining scheduled posts (plus any published after `end`) across [start, end]."""
    now = datetime.now(MUSCAT)
    future = list_future(wp)
    after_end = []
    for post in list_published(wp):
        raw = post.get("date") or ""
        try:
            dt = datetime.fromisoformat(raw).replace(tzinfo=MUSCAT)
        except ValueError:
            continue
        if dt > end:
            after_end.append(post)
    queue = future + after_end
    queue.sort(key=lambda d: (d.get("date") or "", score(d.get("slug") or "")))
    n = len(queue)
    print(
        "backdate",
        start.isoformat(),
        "→",
        end.isoformat(),
        "items",
        n,
        "future",
        len(future),
        "after_end",
        len(after_end),
        flush=True,
    )
    if n == 0:
        return
    span = (end - start).total_seconds()
    step = span / (n - 1) if n > 1 else 0
    published = failed = 0
    for i, post in enumerate(queue):
        when = start + timedelta(seconds=step * i)
        when = when.replace(microsecond=0)
        payload = {
            "date": when.strftime("%Y-%m-%dT%H:%M:%S"),
            "status": "publish" if when <= now else "future",
        }
        code, data, _ = post_retry(wp, f"/wp/v2/posts/{post['id']}", payload)
        if code in (200, 201):
            published += 1
            if published <= 6 or published % 50 == 0:
                print(f"SET {published} {payload['date']} {payload['status']} {post.get('slug')}", flush=True)
        else:
            failed += 1
            print("FAIL", post.get("slug"), code, data, flush=True)
        time.sleep(0.03)
    print(
        json.dumps(
            {
                "moved": published,
                "failed": failed,
                "total": n,
                "first": start.isoformat(),
                "last": end.isoformat(),
            },
            ensure_ascii=False,
        ),
        flush=True,
    )


def reschedule_from_last_published(wp: WP, interval_minutes: int = 1) -> None:
    """Continue from the last published post: 1-minute gaps, publish past/now slots."""
    future = list_future(wp)
    future.sort(key=lambda d: (d.get("date") or "", score(d.get("slug") or "")))
    last = last_published_dt(wp)
    now = datetime.now(MUSCAT).replace(second=0, microsecond=0)
    if last:
        start = last + timedelta(minutes=interval_minutes)
    else:
        start = now + timedelta(minutes=interval_minutes)
    print(
        "from-last",
        last.isoformat() if last else None,
        "start",
        start.isoformat(),
        "future",
        len(future),
        "interval",
        interval_minutes,
        flush=True,
    )
    published = scheduled = failed = 0
    for i, post in enumerate(future):
        when = start + timedelta(minutes=interval_minutes * i)
        payload = {"date": when.strftime("%Y-%m-%dT%H:%M:%S")}
        if when <= now:
            payload["status"] = "publish"
        else:
            payload["status"] = "future"
        code, data, _ = post_retry(wp, f"/wp/v2/posts/{post['id']}", payload)
        if code in (200, 201):
            st = data.get("status") if isinstance(data, dict) else payload["status"]
            if st == "publish" or payload.get("status") == "publish":
                published += 1
                if published <= 8 or published % 25 == 0:
                    print(f"PUBLISH {published} {payload['date']} {post.get('slug')} {st}", flush=True)
            else:
                scheduled += 1
                if scheduled <= 5 or scheduled % 50 == 0:
                    print(f"SCHEDULE {scheduled} {payload['date']} {post.get('slug')} {st}", flush=True)
        else:
            failed += 1
            print("FAIL", post.get("slug"), code, data, flush=True)
        time.sleep(0.03)
    last_when = start + timedelta(minutes=interval_minutes * max(len(future) - 1, 0))
    print(
        json.dumps(
            {
                "published_catchup": published,
                "scheduled": scheduled,
                "failed": failed,
                "total": len(future),
                "start": start.isoformat(),
                "last_slot": last_when.isoformat(),
                "interval_minutes": interval_minutes,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )


def resume_interval(wp: WP, interval_minutes: int = 10) -> None:
    """Re-spread already-scheduled posts, then schedule leftover drafts at a 10-minute cadence."""
    future = list_future(wp)
    drafts = list_drafts(wp)
    print("resume future", len(future), "drafts", len(drafts), "interval", interval_minutes, flush=True)
    future.sort(key=lambda d: score(d.get("slug") or ""))
    drafts.sort(key=lambda d: score(d.get("slug") or ""))
    start = next_slot(minutes=interval_minutes)
    media = cover_id(wp)
    failed = 0
    for i, post in enumerate(future):
        when = start + timedelta(minutes=interval_minutes * i)
        code, data, _ = post_retry(
            wp,
            f"/wp/v2/posts/{post['id']}",
            {"status": "future", "date": when.strftime("%Y-%m-%dT%H:%M:%S")},
        )
        if code not in (200, 201):
            failed += 1
            print("FAIL future", post.get("slug"), code, data, flush=True)
        elif i < 3 or i % 100 == 0:
            print("REDATED", i, when.isoformat(), post.get("slug"), flush=True)
        time.sleep(0.04)
    base = start + timedelta(minutes=interval_minutes * len(future))
    scheduled = 0
    for j, post in enumerate(drafts):
        slug = post.get("slug") or ""
        title = (post.get("title") or {}).get("raw") or slug
        code_c, full, _ = get_retry(wp, f"/wp/v2/posts/{post['id']}", context="edit", _fields="id,content,title,featured_media")
        raw = (full.get("content") or {}).get("raw") or "" if isinstance(full, dict) else ""
        feat = post.get("featured_media") or 0
        if isinstance(full, dict):
            title = (full.get("title") or {}).get("raw") or title
            feat = full.get("featured_media") or feat
        html, seo_title, desc = prepare_content(raw, title, slug)
        when = base + timedelta(minutes=interval_minutes * j)
        payload = {
            "status": "future",
            "date": when.strftime("%Y-%m-%dT%H:%M:%S"),
            "content": html,
            "excerpt": desc,
            "featured_media": feat or media or 0,
            "meta": seo_meta(title, slug, seo_title, desc),
        }
        code, data, _ = post_retry(wp, f"/wp/v2/posts/{post['id']}", payload)
        if code in (200, 201):
            scheduled += 1
            if scheduled <= 3 or scheduled % 50 == 0:
                print("SCHEDULE", scheduled, payload["date"], slug, flush=True)
        else:
            failed += 1
            print("FAIL draft", slug, code, data, flush=True)
        time.sleep(0.04)
    print(json.dumps({"redated": len(future), "scheduled_drafts": scheduled, "failed": failed, "interval_minutes": interval_minutes}, ensure_ascii=False), flush=True)


def main() -> None:
    user = os.environ.get("WP_USER")
    app = os.environ.get("WP_APP_PASSWORD")
    admin_pw = os.environ.get("WP_ADMIN_PASSWORD")
    if not user or not app:
        raise SystemExit("Set WP_USER and WP_APP_PASSWORD")
    wp = WP(os.environ.get("WP_BASE", "https://rukn-eltatawer.com/om"), user, app)
    code, me, _ = wp.get("/wp/v2/users/me", context="edit")
    if code != 200:
        raise SystemExit(f"auth failed {code}: {me}")
    print("auth", me.get("slug"), flush=True)
    if "--backdate-yesterday-to-2pm" in sys.argv:
        start = datetime(2026, 9, 4, 0, 0, tzinfo=MUSCAT)
        end = datetime(2026, 9, 5, 14, 0, tzinfo=MUSCAT)
        backdate_window(wp, start, end)
        code, data, _ = wp.post("/rukn-seo/v1/rebuild", {})
        print("rebuild", code, data)
        return
    if "--every-minute" in sys.argv:
        reschedule_from_last_published(wp, interval_minutes=1)
        code, data, _ = wp.post("/rukn-seo/v1/rebuild", {})
        print("rebuild", code, data)
        return
    wp.post(
        "/wp/v2/settings",
        {
            "title": "ركن التطور عُمان",
            "description": "خدمات منزلية متكاملة في سلطنة عُمان: تنظيف، كشف تسربات، عزل، صيانة وتكييف في مسقط وصلالة وباقي المدن.",
            "timezone": "Asia/Muscat",
            "default_comment_status": "closed",
            "default_ping_status": "closed",
        },
    )
    upsert_snippet(wp)
    publish_privacy(wp)
    if admin_pw:
        admin = Admin(os.environ.get("WP_BASE", "https://rukn-eltatawer.com/om"), user, admin_pw)
        admin.login()
        try:
            fix_theme_schema(admin)
        except Exception as exc:
            print("schema error", exc)
        try:
            code, body, _, final = admin.open(admin.base + "/wp-admin/admin.php?page=rank-math")
            print("rank-math dashboard", code, final[-50:])
        except Exception as exc:
            print("rank-math dashboard error", exc)
    if "--resume" in sys.argv:
        resume_interval(wp, interval_minutes=10)
    else:
        schedule_drafts(wp, publish_first=True, interval_minutes=10)
    # rebuild sitemap if route exists
    code, data, _ = wp.post("/rukn-seo/v1/rebuild", {})
    print("rebuild", code, data)


if __name__ == "__main__":
    main()
