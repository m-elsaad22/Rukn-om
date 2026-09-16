#!/usr/bin/env python3
"""Apply live Oman site repairs (keep UAE WhatsApp, hide call buttons).

  WP_USER, WP_APP_PASSWORD, WP_ADMIN_PASSWORD, WP_BASE
"""

from __future__ import annotations

import html as htmlmod
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from complete_oman_site import (  # noqa: E402
    ensure_menu,
    publish_html_sitemap,
    upsert_page,
    upsert_snippet,
)
from oman_copy import CITIES  # noqa: E402
from seo_fix_oman import (  # noqa: E402
    Admin,
    WP,
    activate_plugin_rest,
    build_plugin_zip,
    flush_permalinks,
    upload_plugin,
)

BASE = os.environ.get("WP_BASE", "https://rukn-eltatawer.com/om").rstrip("/")
WA = os.environ.get("WP_WHATSAPP", "971586634710")


def post_ok(wp: WP, route: str, payload: dict, attempts: int = 4):
    last = (599, {}, {})
    for i in range(attempts):
        last = wp.post(route, payload)
        if last[0] in (200, 201):
            return last
        time.sleep(0.4 * i + 0.3)
    return last


def deactivate_polylang(wp: WP) -> None:
    code, data, _ = wp.post("/wp/v2/plugins/polylang/polylang", {"status": "inactive"})
    print("polylang", code, data.get("status") if isinstance(data, dict) else data, flush=True)


def deactivate_seo_snippet(wp: WP) -> None:
    code, data, _ = wp.get("/code-snippets/v1/snippets", per_page=50)
    if code != 200 or not isinstance(data, list):
        print("snippets list", code, flush=True)
        return
    for item in data:
        name = item.get("name") or ""
        if name == "Rukn Oman SEO core" and item.get("active"):
            wp.request("PUT", f"/code-snippets/v1/snippets/{item['id']}", data={"active": False})
            print("deactivated duplicate SEO snippet", item["id"], flush=True)


def php_string(blob: bytes) -> str:
    import gzip
    import base64

    return base64.b64encode(gzip.compress(blob)).decode("ascii")


def deploy_plugin_via_snippet(wp: WP) -> None:
    plugin_dir = ROOT / "plugins" / "rukn-oman-seo"
    parts = []
    for name in ("rukn-oman-seo.php", "frontend-fix.php", "kayan-blocks.php", "site-structure.php"):
        blob = (plugin_dir / name).read_bytes()
        parts.append(f"'{name}' => '{php_string(blob)}'")
    php = """
$dir = WP_PLUGIN_DIR . '/rukn-oman-seo';
if (!is_dir($dir) && !wp_mkdir_p($dir)) {
    return;
}
$files = [
""" + ",\n".join(parts) + """
];
foreach ($files as $name => $b64) {
    $raw = gzdecode(base64_decode($b64));
    if (!is_string($raw) || $raw === '') {
        continue;
    }
    file_put_contents($dir . '/' . $name, $raw);
}
update_option('rukn_oman_plugin_files', '2.0.2');
if (!function_exists('activate_plugin')) {
    require_once ABSPATH . 'wp-admin/includes/plugin.php';
}
activate_plugin('rukn-oman-seo/rukn-oman-seo.php', '', false, true);
if (class_exists('Rukn_Oman_SEO')) {
    Rukn_Oman_SEO::activate();
}
"""
    payload = {
        "name": "Rukn Oman plugin writer",
        "desc": "Writes rukn-oman-seo plugin files then self-deactivates conceptually via option.",
        "code": php.strip(),
        "scope": "global",
        "active": True,
        "priority": 1,
    }
    code, data, _ = wp.get("/code-snippets/v1/snippets", per_page=50)
    found = None
    if code == 200 and isinstance(data, list):
        for item in data:
            if item.get("name") == "Rukn Oman plugin writer":
                found = item
                break
    if found:
        code, out, _ = wp.request("PUT", f"/code-snippets/v1/snippets/{found['id']}", data=payload)
        print("writer snippet update", code, out.get("id") if isinstance(out, dict) else out, flush=True)
        wp.request("PUT", f"/code-snippets/v1/snippets/{found['id']}", data={"active": True})
    else:
        code, out, _ = wp.post("/code-snippets/v1/snippets", payload)
        print("writer snippet create", code, out.get("id") if isinstance(out, dict) else str(out)[:300], flush=True)
    # Execute by loading front-end.
    import ssl
    import urllib.request

    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        BASE + "/?rukn-deploy=" + str(int(time.time())),
        headers={"User-Agent": "RuknOmanFix/2.0"},
    )
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=60) as r:
            print("writer hit", r.status, flush=True)
    except Exception as e:
        print("writer hit err", e, flush=True)
    time.sleep(1)
    activate_plugin_rest(wp)
    code, data, _ = wp.get("/wp/v2/plugins/rukn-oman-seo/rukn-oman-seo")
    print("plugin after writer", code, data.get("status") if isinstance(data, dict) else data, data.get("version") if isinstance(data, dict) else "", flush=True)
    # Turn writer off so it does not rewrite every request.
    code, data, _ = wp.get("/code-snippets/v1/snippets", per_page=50)
    if code == 200 and isinstance(data, list):
        for item in data:
            if item.get("name") == "Rukn Oman plugin writer" and item.get("active"):
                wp.request("PUT", f"/code-snippets/v1/snippets/{item['id']}", data={"active": False})
                print("writer snippet deactivated", item["id"], flush=True)


def update_structure_snippet(wp: WP, menu_id: int | None) -> None:
    php = (ROOT / "plugins/rukn-oman-seo/site-structure.php").read_text(encoding="utf-8")
    php = php.replace("<?php", "", 1)
    php = php.replace("if (!defined('ABSPATH')) {\n    exit;\n}", "", 1).strip()
    if menu_id:
        php += f"\nupdate_option('rukn_main_menu_id', {int(menu_id)});\n"
    upsert_snippet(wp, php)


def fix_missing_tax(wp: WP) -> None:
    code, data, _ = wp.get("/wp/v2/posts", slug="garage-cleaning-ibri", context="edit")
    if code != 200 or not data:
        print("garage-cleaning-ibri missing", flush=True)
        return
    post = data[0]
    cities = wp.get("/wp/v2/cities", slug="ibri")
    cats = wp.get("/wp/v2/service_categories", slug="cleaning-services")
    city_id = cities[1][0]["id"] if cities[0] == 200 and cities[1] else None
    cat_id = cats[1][0]["id"] if cats[0] == 200 and cats[1] else None
    payload = {}
    if city_id:
        payload["cities"] = [city_id]
    if cat_id:
        payload["service_categories"] = [cat_id]
    if payload:
        code, out, _ = post_ok(wp, f"/wp/v2/posts/{post['id']}", payload)
        print("garage tax", code, payload, flush=True)


def enrich_services(wp: WP) -> None:
    code, svcs, _ = wp.get("/wp/v2/services", per_page=100, context="edit", status="publish")
    if code != 200 or not isinstance(svcs, list):
        print("services list", code, flush=True)
        return
    city_links = "".join(
        f'<li><a href="/om/city/{slug}/">{info["ar"]}</a></li>'
        for slug, info in CITIES.items()
    )
    for s in svcs:
        title = (s.get("title") or {}).get("raw") or s.get("slug")
        slug = s.get("slug")
        muscat = f"/om/{slug}-muscat/" if slug else "/om/our-services/"
        html = f"""
<section>
<h2>{htmlmod.escape(title)} في سلطنة عُمان</h2>
<p>فريق ركن التطور يقدّم هذه الخدمة داخل مدن التغطية بعد معاينة ميدانية. التسعير بالريال العُماني، والتواصل عبر واتساب.</p>
<p><a href="{muscat}">دليل الخدمة في مسقط</a> · <a href="/om/our-services/">كل التصنيفات</a></p>
<h3>المدن</h3>
<ul>{city_links}</ul>
<p><a href="https://wa.me/{WA}" rel="noopener">اطلب المعاينة عبر واتساب</a></p>
</section>
"""
        post_ok(
            wp,
            f"/wp/v2/services/{s['id']}",
            {
                "content": html,
                "featured_media": 245,
                "comment_status": "closed",
            },
        )
        print("service", slug, flush=True)


def update_contact_page(wp: WP) -> None:
    city_lis = "".join(
        f'<li><a href="/om/city/{slug}/">خدماتنا في {info["ar"]}</a></li>'
        for slug, info in CITIES.items()
    )
    html = f"""
<section>
<h2>تواصل عبر واتساب — ركن التطور عُمان</h2>
<p>لطلب معاينة أو استفسار عن خدمة في أي من مدن التغطية راسلنا على واتساب. لا نضع زر اتصال هاتفي على الموقع.</p>
<p><a class="btn btn-wa" href="https://wa.me/{WA}" rel="noopener">واتساب {WA}</a></p>
<ul>
<li>واتساب: <a href="https://wa.me/{WA}" rel="noopener">+{WA}</a></li>
<li>البريد: admin@rukn-eltatawer.com</li>
<li>ساعات العمل: السبت–الخميس 08:00–21:00 بتوقيت مسقط</li>
</ul>
<h3>المدن</h3>
<ul>{city_lis}</ul>
<p>لا نسعّر الأعمال المعقّدة دون معاينة. الفني يزور الموقع ثم يكتب السعر بالريال العُماني.</p>
</section>
"""
    upsert_page(
        wp,
        "contact",
        "اتصل بنا",
        html,
        "تواصل مع ركن التطور عُمان عبر واتساب لتحديد معاينة في مدينتك.",
        "Contact Rukn Eltatawer Oman on WhatsApp",
        f"<section><h2>WhatsApp us in Oman</h2><p><a href='https://wa.me/{WA}'>WhatsApp</a></p></section>",
    )


def update_info_pages(wp: WP) -> None:
    wa = f"https://wa.me/{WA}"
    about = f"""
<section>
<h2>من نحن — ركن التطور عُمان</h2>
<p>ركن التطور فريق خدمات منزلية يعمل داخل سلطنة عُمان: مسقط، صلالة، نزوى، صحار، صور، البريمي، عبري والرستاق. لسنا نسخة من صفحة إمارة أخرى؛ المعاينة ميدانية والتسعير بالريال العُماني.</p>
<p>نغطي كشف التسربات بدون تكسير، العزل، السباكة، التكييف والكهرباء، التنظيف، مكافحة الحشرات، الحدائق، الصبغ والصيانة العامة.</p>
<h3>كيف نعمل</h3>
<ul>
<li>تواصل عبر واتساب فقط — لا يوجد زر اتصال هاتفي على الموقع.</li>
<li>نحدد موعد معاينة في المدينة المطلوبة.</li>
<li>تستلم عرض سعر مكتوباً قبل التنفيذ.</li>
</ul>
<p><a href="/om/contact/">صفحة التواصل</a> · <a href="/om/our-services/">الخدمات</a> · <a href="/om/cities/">المدن</a></p>
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
<p>واتساب عبر <a href="{wa}" rel="noopener">+{WA}</a>، ونحدد موعد المعاينة. لا يوجد زر اتصال هاتفي على الموقع.</p>
<h3>هل يوجد ضمان؟</h3>
<p>يُذكر في عرض السعر حسب الخدمة والخامة.</p>
</section>
"""
    upsert_page(
        wp,
        "about",
        "من نحن",
        about.strip(),
        "ركن التطور فريق خدمات منزلية في سلطنة عُمان: تنظيف، تسربات، عزل وصيانة في مسقط وباقي المدن.",
        "About Rukn Eltatawer Oman",
        "<section><h2>About us</h2><p>Rukn Eltatawer is a home-services team in the Sultanate of Oman. WhatsApp only — no phone-call button on the site. Site visit first, then a written quote in Omani rial.</p></section>",
    )
    upsert_page(
        wp,
        "faq",
        "الأسئلة الشائعة",
        faq.strip(),
        "أسئلة شائعة عن خدمات ركن التطور في سلطنة عُمان والتواصل عبر واتساب.",
        "FAQ — Rukn Eltatawer Oman",
        f"<section><h2>FAQ</h2><p>WhatsApp {WA} to book a site visit. Quotes are in Omani rial after inspection.</p></section>",
    )


def pages_ids(wp: WP) -> dict[str, int]:
    out = {}
    code, pages, _ = wp.get("/wp/v2/pages", per_page=50, status="publish")
    if code == 200 and isinstance(pages, list):
        for p in pages:
            out[p.get("slug")] = p["id"]
    return out


def purge(wp: WP) -> None:
    code, data, _ = wp.post("/rukn-seo/v1/rebuild", {})
    print("rebuild", code, data, flush=True)
    wp.post("/litespeed/v1/purge_all", {})
    print("litespeed purge attempted", flush=True)


def verify() -> None:
    import ssl
    import urllib.error
    import urllib.request

    class NoRedir(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    ctx = ssl.create_default_context()
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx), NoRedir)
    checks = [
        ("https://rukn-eltatawer.com/om/city/muscat/", "city", 200),
        ("https://rukn-eltatawer.com/om/service-category/cleaning-services/", "cat", 200),
        ("https://rukn-eltatawer.com/om/services/water-leak-detection/", "svc", 200),
        ("https://rukn-eltatawer.com/om/en/", "en", 200),
        ("https://rukn-eltatawer.com/om/contact-us/", "contact-us", 301),
        ("https://rukn-eltatawer.com/om/blog/", "blog", 301),
        ("https://rukn-eltatawer.com/om/this-page-does-not-exist-xyz/", "404", 404),
        ("https://rukn-eltatawer.com/om/contact/", "contact", 200),
        ("https://rukn-eltatawer.com/om/", "home", 200),
        ("https://rukn-eltatawer.com/om/home-cleaning-muscat/", "article", 200),
    ]
    for url, label, expect in checks:
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "RuknOmanFix/2.0"})
        try:
            with opener.open(req, timeout=30) as r:
                body = r.read().decode("utf-8", "replace")
                tel = bool(re.search(r'''href=["']tel:''', body))
                empty_nav = 'nav class="menu"></nav>' in body
                hide = "rukn-hide-call" in body and "<body" in body
                wa = "971586634710" in body
                print(label, "OK", r.status, "expect", expect, "tel", tel, "empty_nav", empty_nav, "hide", hide, "wa", wa, flush=True)
        except urllib.error.HTTPError as e:
            loc = e.headers.get("Location", "") if e.headers else ""
            print(label, "HTTP", e.code, "expect", expect, "loc", loc, flush=True)
        except Exception as e:
            print(label, "ERR", e, flush=True)


def main() -> None:
    user = os.environ.get("WP_USER")
    app = os.environ.get("WP_APP_PASSWORD")
    admin_pw = os.environ.get("WP_ADMIN_PASSWORD") or os.environ.get("WP_PASSWORD")
    if not user or not app:
        raise SystemExit("Set WP_USER and WP_APP_PASSWORD")
    wp = WP(BASE, user, app)
    code, me, _ = wp.get("/wp/v2/users/me", context="edit")
    if code != 200:
        raise SystemExit(f"auth failed {code}: {me}")
    print("auth", me.get("slug"), me.get("roles"), flush=True)

    deactivate_polylang(wp)
    deploy_plugin_via_snippet(wp)

    if admin_pw:
        zip_path = build_plugin_zip(ROOT / "plugins" / "rukn-oman-seo.zip")
        admin = Admin(BASE, user, admin_pw)
        admin.login()
        upload_plugin(admin, zip_path)
        activate_plugin_rest(wp)
        flush_permalinks(admin)
    else:
        activate_plugin_rest(wp)

    deactivate_seo_snippet(wp)
    ids = pages_ids(wp)
    menu_id = 0
    needed = ("our-services", "cities", "about", "faq", "contact", "html-sitemap")
    if all(k in ids for k in needed):
        menu_id = ensure_menu(wp, ids)
    else:
        print("menu skipped missing pages", [k for k in needed if k not in ids], flush=True)
    update_structure_snippet(wp, menu_id)
    update_contact_page(wp)
    update_info_pages(wp)
    ids = pages_ids(wp)
    publish_html_sitemap(wp)
    if menu_id:
        update_structure_snippet(wp, menu_id)

    wp.post(
        "/wp/v2/settings",
        {
            "title": "ركن التطور عُمان",
            "timezone": "Asia/Muscat",
            "default_comment_status": "closed",
            "default_ping_status": "closed",
        },
    )

    fix_missing_tax(wp)
    enrich_services(wp)
    code, bulk, _ = wp.post("/rukn-seo/v1/bulk-fix", {})
    print("bulk-fix", code, bulk, flush=True)
    purge(wp)
    time.sleep(3)
    verify()


if __name__ == "__main__":
    main()
