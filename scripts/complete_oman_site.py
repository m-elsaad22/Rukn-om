#!/usr/bin/env python3
"""Complete Oman site structure: taxonomies, pages, menu, duplicates, content errors.

Credentials from the environment (never committed):
  WP_USER, WP_APP_PASSWORD, WP_BASE
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from oman_copy import CITIES  # noqa: E402
from publish_schedule_oman import (  # noqa: E402
    PHONE,
    WHATSAPP,
    get_retry,
    post_retry,
    prepare_content,
    seo_meta,
    split_slug,
)
from seo_fix_oman import WP  # noqa: E402

BASE = os.environ.get("WP_BASE", "https://rukn-eltatawer.com/om").rstrip("/")
DUPLICATE_SERVICES = {"grass-wall", "artificial-grass-grdn"}

SERVICE_CATS = [
    ("leak-detection", "كشف التسربات", "كشف تسربات المياه والغاز والتكييف بدون تكسير في مدن سلطنة عُمان، مع تقرير بعد المعاينة."),
    ("insulation", "العزل", "عزل أسطح وخزانات وحمامات مائي وحراري يناسب مناخ السلطنة."),
    ("general-maintenance", "الصيانة العامة", "صيانة منازل ومبانٍ وأجهزة بفريق واحد داخل سلطنة عُمان."),
    ("plumbing", "السباكة والتسليك", "سباكة، تسليك مجاري، سخانات ومضخات مياه بأسعار بالريال العُماني."),
    ("ac-electrical", "التكييف والكهرباء", "تركيب وصيانة التكييف، فريون، أعطال كهرباء ولوحات."),
    ("cleaning-services", "خدمات التنظيف", "تنظيف منازل وفلل ومكاتب وخزانات وواجهات في مسقط وباقي المدن."),
    ("pest-control", "مكافحة الحشرات", "مكافحة صراصير ونمل وقوارض بأمان مع متابعة بعد التنفيذ."),
    ("gardens-pools", "الحدائق والمسابح", "تنسيق حدائق، عشب، ري، مسابح ونوافير."),
    ("painting-decor", "الصبغ والديكورات", "صبغ داخلي وخارجي، جبس، ورق جدران وتشطيب."),
]

CAT_RULES = [
    (("water-leak", "gas-leak", "ac-leak", "leak-detection", "leak"), "leak-detection"),
    (("split-ac", "central-ac", "window-ac", "solar-ac", "ac-", "freon", "cooling", "refrigeration", "duct-maintenance", "duct-cleaning"), "ac-electrical"),
    (("electric", "electrician", "wiring", "cctv", "electric-panel"), "ac-electrical"),
    (("plumb", "drain", "septic", "sewer", "water-heater", "water-pump", "water-pumps", "sanitary", "unclog"), "plumbing"),
    (("insulat", "waterproof", "humidity", "soundproof", "tank-lining", "tank-insulation"), "insulation"),
    (("pest", "cockroach", "termite", "bed-bug", "rodent", "ant-control", "mosquito", "fly-control", "crawling-pest", "flying-pest"), "pest-control"),
    (("clean", "steriliz", "marble-polish", "deep-cleaning", "moquette", "sofa", "curtain", "mattress"), "cleaning-services"),
    (("paint", "gypsum", "decor", "wallpaper", "renovation", "finishing", "crack", "epoxy"), "painting-decor"),
    (("garden", "grass", "landscap", "pool", "irrigation", "pergola", "arbor", "fountain", "shades"), "gardens-pools"),
    (("maintenance", "building-maintenance", "general-maintenance"), "general-maintenance"),
]


def cat_for(service: str) -> str:
    s = (service or "").lower()
    for prefixes, slug in CAT_RULES:
        if any(s.startswith(p) or p in s for p in prefixes):
            return slug
    return "general-maintenance"


def retry_delete(wp: WP, route: str, attempts: int = 4):
    last = (599, {}, {})
    for i in range(attempts):
        last = wp.delete(route, force="false")
        if last[0] in (200, 201):
            return last
        time.sleep(0.8 * i + 0.4)
    return last


def upsert_term(wp: WP, route: str, slug: str, name: str, description: str) -> int:
    code, data, _ = wp.get(route, slug=slug, per_page=20)
    payload = {"name": name, "slug": slug, "description": description}
    if code == 200 and isinstance(data, list) and data:
        tid = data[0]["id"]
        code, out, _ = wp.post(f"{route}/{tid}", payload)
        print("term update", slug, code, tid, flush=True)
        return tid
    code, out, _ = wp.post(route, payload)
    tid = out.get("id") if isinstance(out, dict) else None
    print("term create", slug, code, tid, flush=True)
    if not tid:
        raise RuntimeError(f"term failed {slug} {code} {out}")
    return int(tid)


def upsert_page(wp: WP, slug: str, title: str, html: str, excerpt: str, en_title: str, en_html: str) -> int:
    code, data, _ = wp.get("/wp/v2/pages", slug=slug, status="any", context="edit", per_page=5)
    payload = {
        "title": title,
        "slug": slug,
        "status": "publish",
        "content": html,
        "excerpt": excerpt,
        "comment_status": "closed",
        "meta": {
            "rank_math_title": f"{title} | ركن التطور عُمان",
            "rank_math_description": excerpt[:160],
            "_rukn_lang": "ar",
            "_rukn_en_title": en_title,
            "_rukn_en_content": en_html,
            "_rukn_en_desc": (en_title + ". Site visit then a written OMR quote.")[:160],
        },
    }
    if code == 200 and isinstance(data, list) and data:
        pid = data[0]["id"]
        code, out, _ = post_retry(wp, f"/wp/v2/pages/{pid}", payload)
        print("page update", slug, code, out.get("link") if isinstance(out, dict) else out, flush=True)
        return int(pid)
    code, out, _ = post_retry(wp, "/wp/v2/pages", payload)
    print("page create", slug, code, out.get("link") if isinstance(out, dict) else out, flush=True)
    return int(out["id"])


def page_htmls() -> dict[str, dict]:
    city_lis = "".join(
        f'<li><a href="/om/city/{slug}/">خدماتنا في {info["ar"]}</a> — {info["gov_ar"]}</li>'
        for slug, info in CITIES.items()
    )
    cat_lis = "".join(
        f'<li><a href="/om/service-category/{slug}/">{name}</a></li>'
        for slug, name, _d in SERVICE_CATS
    )
    wa = f"https://wa.me/{WHATSAPP}"
    about = f"""
<section>
<h2>من نحن — ركن التطور عُمان</h2>
<p>ركن التطور فريق خدمات منزلية يعمل داخل سلطنة عُمان: مسقط، صلالة، نزوى، صحار، صور، البريمي، عبري والرستاق. لسنا نسخة من صفحة إمارة أخرى؛ المعاينة ميدانية والتسعير بالريال العُماني.</p>
<p>نغطي كشف التسربات بدون تكسير، العزل، السباكة، التكييف والكهرباء، التنظيف، مكافحة الحشرات، الحدائق، الصبغ والصيانة العامة.</p>
<h3>كيف نعمل</h3>
<ul>
<li>تواصل عبر واتساب أو اتصال على {PHONE}.</li>
<li>نحدد موعد معاينة في المدينة المطلوبة.</li>
<li>تستلم عرض سعر مكتوباً قبل التنفيذ.</li>
</ul>
<p><a href="/om/contact/">صفحة التواصل</a> · <a href="/om/our-services/">الخدمات</a> · <a href="/om/cities/">المدن</a></p>
</section>
"""
    contact = f"""
<section>
<h2>اتصل بنا في سلطنة عُمان</h2>
<p>لطلب معاينة أو استفسار عن خدمة في أي من مدن التغطية:</p>
<ul>
<li>هاتف: <a href="tel:{PHONE}">{PHONE}</a></li>
<li>واتساب: <a href="{wa}" rel="noopener">{PHONE}</a></li>
<li>البريد: admin@rukn-eltatawer.com</li>
<li>ساعات العمل: السبت–الخميس 08:00–21:00 بتوقيت مسقط</li>
</ul>
<h3>المدن</h3>
<ul>{city_lis}</ul>
<p>لا نسعّر الأعمال المعقّدة عبر الهاتف. الفني يزور الموقع ثم يكتب السعر بالريال العُماني.</p>
</section>
"""
    services = f"""
<section>
<h2>خدمات ركن التطور في عُمان</h2>
<p>اختر التصنيف ثم المدينة. كل مقال مربوط بتصنيفه ومدينته، والموعد يُؤكد بعد المعاينة.</p>
<h3>التصنيفات</h3>
<ul>{cat_lis}</ul>
<h3>المدن</h3>
<ul>{city_lis}</ul>
<p>أرقام التواصل في <a href="/om/contact/">اتصل بنا</a>.</p>
</section>
"""
    cities = f"""
<section>
<h2>المدن التي نغطيها في سلطنة عُمان</h2>
<p>فريق ميداني في ثماني مدن. اضغط المدينة لعرض الخدمات المرتبطة بها.</p>
<ul>{city_lis}</ul>
<p>التصنيفات: <a href="/om/our-services/">كل الخدمات</a>.</p>
</section>
"""
    faq = f"""
<section>
<h2>أسئلة شائعة</h2>
<h3>هل تكشفون التسرب بدون تكسير؟</h3>
<p>نعم. نستخدم أجهزة كشف وكاميرا حرارية عند الحاجة، ثم تقرير يوضح المصدر قبل أي تكسير.</p>
<h3>ما المدن؟</h3>
<p>مسقط، صلالة، نزوى، صحار، صور، البريمي، عبري والرستاق.</p>
<h3>هل السعر بالريال العُماني؟</h3>
<p>نعم بعد المعاينة. لا نكتب السعر بعملة دولة أخرى.</p>
<h3>كيف أطلب؟</h3>
<p>واتساب أو اتصال على {PHONE}، ونحدد موعد المعاينة.</p>
<h3>هل يوجد ضمان؟</h3>
<p>يُذكر في عرض السعر حسب الخدمة والخامة.</p>
</section>
"""
    terms = """
<section>
<h2>الشروط والأحكام</h2>
<p>تنطبق هذه الشروط على طلبات الخدمة عبر موقع ركن التطور عُمان أو واتساب.</p>
<h3>المعاينة والعرض</h3>
<p>العرض المكتوب بعد المعاينة هو المعتمد. أي تعديل على نطاق العمل يُحدَّث كتابياً.</p>
<h3>الأسعار</h3>
<p>التسعير بالريال العُماني. لا يشمل أعمالاً لم تُذكر في العرض.</p>
<h3>المواعيد</h3>
<p>نؤكد الموعد صباح التنفيذ عند الطرق أو الطقس في الأودية والجبال.</p>
<h3>البيانات</h3>
<p>تفاصيل التعامل مع البيانات في <a href="/om/privacy-policy/">سياسة الخصوصية</a>.</p>
</section>
"""
    return {
        "about": {
            "title": "من نحن",
            "excerpt": "ركن التطور فريق خدمات منزلية في سلطنة عُمان: تنظيف، تسربات، عزل وصيانة في مسقط وباقي المدن.",
            "html": about.strip(),
            "en_title": "About Rukn Eltatawer Oman",
            "en_html": "<section><h2>About us</h2><p>Rukn Eltatawer is a home-services team in the Sultanate of Oman. Site visit first, then a written quote in Omani rial.</p></section>",
        },
        "contact": {
            "title": "اتصل بنا",
            "excerpt": f"تواصل مع ركن التطور عُمان على {PHONE} أو واتساب لتحديد معاينة في مدينتك.",
            "html": contact.strip(),
            "en_title": "Contact Rukn Eltatawer Oman",
            "en_html": f"<section><h2>Contact</h2><p>Call or WhatsApp {PHONE}. We cover Muscat, Salalah, Nizwa, Sohar, Sur, Al Buraimi, Ibri and Rustaq.</p></section>",
        },
        "our-services": {
            "title": "خدماتنا",
            "excerpt": "تصنيفات خدمات ركن التطور في عُمان: تسربات، عزل، سباكة، تكييف، تنظيف، حشرات، حدائق وصبغ.",
            "html": services.strip(),
            "en_title": "Our services in Oman",
            "en_html": "<section><h2>Services</h2><p>Leak detection, insulation, plumbing, AC, cleaning, pest control, gardens and painting across Oman cities.</p></section>",
        },
        "cities": {
            "title": "المدن",
            "excerpt": "تغطية ركن التطور: مسقط، صلالة، نزوى، صحار، صور، البريمي، عبري والرستاق.",
            "html": cities.strip(),
            "en_title": "Cities we cover in Oman",
            "en_html": "<section><h2>Cities</h2><p>Muscat, Salalah, Nizwa, Sohar, Sur, Al Buraimi, Ibri and Rustaq.</p></section>",
        },
        "faq": {
            "title": "الأسئلة الشائعة",
            "excerpt": "إجابات عن المعاينة، المدن، الريال العُماني، والضمان في خدمات ركن التطور عُمان.",
            "html": faq.strip(),
            "en_title": "Frequently asked questions",
            "en_html": "<section><h2>FAQ</h2><p>We survey the site before quoting in OMR. Coverage is eight Oman cities.</p></section>",
        },
        "terms": {
            "title": "الشروط والأحكام",
            "excerpt": "شروط طلب الخدمة والمعاينة والتسعير بالريال العُماني لدى ركن التطور عُمان.",
            "html": terms.strip(),
            "en_title": "Terms of service",
            "en_html": "<section><h2>Terms</h2><p>The written quote after the site visit is binding. Prices are in Omani rial.</p></section>",
        },
    }


def patch_seo_snippet_terms(wp: WP) -> None:
    code, data, _ = wp.get("/code-snippets/v1/snippets/5")
    if code != 200 or not isinstance(data, dict):
        print("seo snippet fetch", code, flush=True)
        return
    src = data.get("code") or ""
    if "WP_Term" in src and "numberposts' => 2500" in src:
        print("seo snippet already has term SEO", flush=True)
        return
    old_post = "        $post = get_queried_object();\n        if ($post instanceof WP_Post) {"
    new_post = """        $obj = get_queried_object();
        if ($obj instanceof WP_Term) {
            $link = get_term_link($obj);
            if (is_wp_error($link)) { $link = home_url('/'); }
            $desc = wp_strip_all_tags($obj->description ?: '');
            $title = ($obj->name . ' | ركن التطور عُمان');
            if ($desc === '') {
                $desc = 'خدمات ركن التطور في ' . $obj->name . ' داخل سلطنة عُمان. معاينة ثم سعر بالريال العُماني.';
            }
            return [
                'title' => $title,
                'desc' => wp_html_excerpt($desc, 160),
                'canonical' => $link,
                'lang' => 'ar-OM',
                'hreflang' => [['ar-OM', $link], ['x-default', $link]],
            ];
        }
        $post = $obj;
        if ($post instanceof WP_Post) {"""
    if old_post in src:
        src = src.replace(old_post, new_post, 1)
    src = src.replace("'numberposts' => 500", "'numberposts' => 2500")
    if "taxonomy' => $tax" not in src:
        needle = "        $posts = get_posts(["
        inject = """        foreach (['cities', 'service_categories'] as $tax) {
            $terms = get_terms(['taxonomy' => $tax, 'hide_empty' => false, 'number' => 50]);
            if (!is_wp_error($terms) && $terms) {
                foreach ($terms as $term) {
                    $link = get_term_link($term);
                    if (!is_wp_error($link)) {
                        $urls[] = [$link, '0.7', 'weekly', gmdate('c')];
                    }
                }
            }
        }
        $posts = get_posts(["""
        if needle in src:
            src = src.replace(needle, inject, 1)
    payload = {"code": src, "active": True}
    code, out, _ = wp.request("PUT", "/code-snippets/v1/snippets/5", data=payload)
    print("seo snippet patch", code, "len", len(src), flush=True)


def upsert_snippet(wp: WP, code_php: str) -> None:
    code, data, _ = wp.get("/code-snippets/v1/snippets", per_page=50)
    found = None
    if code == 200 and isinstance(data, list):
        for item in data:
            if item.get("name") == "Rukn Oman site structure":
                found = item
                break
    payload = {
        "name": "Rukn Oman site structure",
        "desc": "Post taxonomies, /services/ redirects, city archives, main menu location",
        "code": code_php,
        "scope": "global",
        "active": True,
        "priority": 8,
    }
    if found:
        code, out, _ = wp.request("PUT", f"/code-snippets/v1/snippets/{found['id']}", data=payload)
        print("structure snippet update", code, out.get("active") if isinstance(out, dict) else out, flush=True)
        if isinstance(out, dict) and not out.get("active"):
            wp.request("PUT", f"/code-snippets/v1/snippets/{found['id']}", data={"active": True})
            print("structure snippet reactivated", flush=True)
    else:
        code, out, _ = wp.post("/code-snippets/v1/snippets", payload)
        print("structure snippet create", code, out.get("id") if isinstance(out, dict) else out, flush=True)


def ensure_menu(wp: WP, page_ids: dict[str, int]) -> int:
    code, menus, _ = wp.get("/wp/v2/menus", per_page=50)
    menu = None
    if code == 200 and isinstance(menus, list):
        for m in menus:
            if m.get("slug") in {"rukn-main", "main-menu-rukn"} or m.get("name") == "القائمة الرئيسية":
                menu = m
                break
    payload = {"name": "القائمة الرئيسية", "slug": "rukn-main", "auto_add": False}
    if menu:
        mid = menu["id"]
        wp.post(f"/wp/v2/menus/{mid}", payload)
    else:
        code, menu, _ = wp.post("/wp/v2/menus", payload)
        mid = menu.get("id") if isinstance(menu, dict) else None
        print("menu create", code, mid, flush=True)
    if not mid:
        print("menu failed", menu, flush=True)
        return 0
    code, items, _ = wp.get("/wp/v2/menu-items", menus=mid, per_page=50, context="edit")
    if code == 200 and isinstance(items, list):
        for it in items:
            wp.delete(f"/wp/v2/menu-items/{it['id']}", force="true")
    entries = [
        ("الرئيسية", "custom", 0, f"{BASE}/"),
        ("خدماتنا", "post_type", page_ids["our-services"], ""),
        ("المدن", "post_type", page_ids["cities"], ""),
        ("من نحن", "post_type", page_ids["about"], ""),
        ("الأسئلة الشائعة", "post_type", page_ids["faq"], ""),
        ("اتصل بنا", "post_type", page_ids["contact"], ""),
    ]
    for i, (title, typ, oid, url) in enumerate(entries, 1):
        body = {
            "title": title,
            "status": "publish",
            "menus": mid,
            "menu_order": i,
            "type": typ,
            "parent": 0,
        }
        if typ == "custom":
            body["url"] = url
            body["object"] = "custom"
        else:
            body["object"] = "page"
            body["object_id"] = oid
        code, out, _ = wp.post("/wp/v2/menu-items", body)
        print("menu item", title, code, flush=True)
    # store menu id via a tiny snippet option using REST settings is not available;
    # the structure snippet reads rukn_main_menu_id — set via Code Snippets is elsewhere.
    # Use a dedicated option through a one-off PHP in the same snippet after rewrite below.
    return int(mid)


def list_all_posts(wp: WP) -> list[dict]:
    items = []
    page = 1
    while True:
        code, data, hdrs = wp.get(
            "/wp/v2/posts",
            status="publish,future,draft",
            per_page=100,
            page=page,
            context="edit",
            _fields="id,slug,title,status,cities,featured_media",
        )
        if code != 200 or not isinstance(data, list) or not data:
            break
        items.extend(data)
        pages = int(hdrs.get("X-WP-TotalPages") or hdrs.get("x-wp-totalpages") or 1)
        if page >= pages:
            break
        page += 1
    return items


def strip_broken_images(html: str) -> str:
    html = re.sub(r"<img[^>]+src=[\"']service-[^\"']+[\"'][^>]*>", "", html, flags=re.I)
    html = re.sub(r"<img[^>]+src=[\"'](?!https?:)[^\"']+[\"'][^>]*>", "", html, flags=re.I)
    return html


def extra_faqs(wp: WP) -> None:
    extras = [
        ("هل تعملون في جميع محافظات السلطنة؟", "نغطي ثماني مدن محورية ونرتب الزيارة حسب الجدول الميداني داخل سلطنة عُمان."),
        ("هل تكتبون العقد أو العرض بالريال العُماني؟", "نعم. السعر بعد المعاينة بالريال العُماني وليس بعملة دولة أخرى."),
        ("هل يمكن دمج أكثر من خدمة في زيارة واحدة؟", "نعم عند الاتفاق مسبقاً، مثلاً كشف تسرب مع عزل أو تنظيف مع مكافحة."),
    ]
    for q, a in extras:
        code, found, _ = wp.get("/wp/v2/faqs", search=q, per_page=10, status="any")
        exists = False
        if code == 200 and isinstance(found, list):
            exists = any((x.get("title") or {}).get("raw") == q or (x.get("title") or {}).get("rendered") == q for x in found)
        if exists:
            continue
        code, out, _ = wp.post("/wp/v2/faqs", {"title": q, "status": "publish", "content": f"<p>{a}</p>"})
        print("faq", code, q[:40], flush=True)


def main() -> None:
    user = os.environ.get("WP_USER")
    app = os.environ.get("WP_APP_PASSWORD")
    if not user or not app:
        raise SystemExit("Set WP_USER and WP_APP_PASSWORD")
    wp = WP(BASE, user, app)
    code, me, _ = wp.get("/wp/v2/users/me", context="edit")
    if code != 200:
        raise SystemExit(f"auth failed {code}: {me}")
    print("auth", me.get("slug"), flush=True)
    patch_seo_snippet_terms(wp)

    snippet_path = Path(__file__).resolve().parents[1] / "plugins" / "rukn-oman-seo" / "site-structure.php"
    php = snippet_path.read_text()
    php = php.replace("<?php", "").replace("if (!defined('ABSPATH')) {\n    exit;\n}", "", 1).strip()
    upsert_snippet(wp, php)

    wp.post(
        "/wp/v2/settings",
        {
            "title": "ركن التطور عُمان",
            "description": "خدمات منزلية متكاملة في سلطنة عُمان: تنظيف، كشف تسربات، عزل، صيانة وتكييف في مسقط وصلالة وباقي المدن.",
            "timezone": "Asia/Muscat",
            "default_comment_status": "closed",
            "default_ping_status": "closed",
            "posts_per_page": 16,
        },
    )

    city_ids = {}
    for slug, info in CITIES.items():
        desc = (
            f"ركن التطور في {info['ar']} داخل {info['gov_ar']}. {info['note_ar']}. "
            f"التغطية: {info['areas_ar']}. {info['climate_ar']}. التسعير بالريال العُماني بعد المعاينة."
        )
        city_ids[slug] = upsert_term(wp, "/wp/v2/cities", slug, info["ar"], desc)

    cat_ids = {}
    for slug, name, desc in SERVICE_CATS:
        cat_ids[slug] = upsert_term(wp, "/wp/v2/service_categories", slug, name, desc)

    pages = page_htmls()
    page_ids = {}
    for slug, spec in pages.items():
        page_ids[slug] = upsert_page(
            wp, slug, spec["title"], spec["html"], spec["excerpt"], spec["en_title"], spec["en_html"]
        )

    extra_faqs(wp)
    menu_id = ensure_menu(wp, page_ids)
    if menu_id:
        php_with_menu = php + f"\nupdate_option('rukn_main_menu_id', {int(menu_id)});\n"
        upsert_snippet(wp, php_with_menu)
        print("menu id stored", menu_id, flush=True)

    posts = list_all_posts(wp)
    print("posts", len(posts), flush=True)
    deleted = 0
    for post in posts:
        slug = post.get("slug") or ""
        service, _city = split_slug(slug)
        if service in DUPLICATE_SERVICES:
            code, data, _ = retry_delete(wp, f"/wp/v2/posts/{post['id']}")
            print("TRASH dup", slug, code, flush=True)
            deleted += code in (200, 201)
            time.sleep(0.05)
    if deleted:
        posts = list_all_posts(wp)
        print("after trash", len(posts), "deleted", deleted, flush=True)

    assigned = fixed = failed = skipped = 0
    for i, post in enumerate(posts, 1):
        slug = post.get("slug") or ""
        service, city = split_slug(slug)
        city_id = city_ids.get(city)
        cat_id = cat_ids.get(cat_for(service))
        title = (post.get("title") or {}).get("raw") or slug
        code_c, full, _ = get_retry(
            wp,
            f"/wp/v2/posts/{post['id']}",
            context="edit",
            _fields="id,content,title,cities,service_categories,featured_media",
        )
        raw = ""
        feat = post.get("featured_media") or 0
        have_city = bool(post.get("cities"))
        have_cat = False
        if code_c == 200 and isinstance(full, dict):
            raw = (full.get("content") or {}).get("raw") or ""
            title = (full.get("title") or {}).get("raw") or title
            feat = full.get("featured_media") or feat
            have_city = bool(full.get("cities"))
            have_cat = bool(full.get("service_categories"))
        needs_content = (
            "{PHONE" in raw
            or "{WHATSAPP" in raw
            or "service-" in raw
            or "rukn-local-start" not in raw
            or "<h1" in raw.lower()
        )
        payload = {
            "cities": [city_id] if city_id else [],
            "service_categories": [cat_id] if cat_id else [],
            "featured_media": feat or 0,
        }
        if needs_content:
            html, seo_title, desc = prepare_content(raw, title, slug)
            html = strip_broken_images(html)
            payload["content"] = html
            payload["excerpt"] = desc
            payload["meta"] = seo_meta(title, slug, seo_title, desc)
            fixed += 1
        elif have_city and have_cat:
            skipped += 1
            if i % 200 == 0:
                print(f"skip {i}/{len(posts)} {slug}", flush=True)
            continue
        code, data, _ = post_retry(wp, f"/wp/v2/posts/{post['id']}", payload)
        if code == 400 and "service_categories" in payload:
            payload.pop("service_categories", None)
            code, data, _ = post_retry(wp, f"/wp/v2/posts/{post['id']}", payload)
        if code in (200, 201):
            assigned += 1
            if assigned <= 5 or assigned % 50 == 0:
                print(f"OK {assigned} {slug} city={city} cat={cat_for(service)}", flush=True)
        else:
            failed += 1
            print("FAIL", slug, code, data, flush=True)
        time.sleep(0.03)

    code, rebuild, _ = wp.post("/rukn-seo/v1/rebuild", {})
    print("rebuild", code, rebuild, flush=True)
    print(
        json.dumps(
            {
                "assigned": assigned,
                "content_fixed": fixed,
                "skipped": skipped,
                "failed": failed,
                "deleted_dupes": deleted,
                "pages": page_ids,
                "menu_id": menu_id,
                "cities": city_ids,
                "categories": cat_ids,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
