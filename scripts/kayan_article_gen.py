"""Build a unique Kayan-ready Arabic article for one Oman service × city post."""

from __future__ import annotations

import hashlib
import random
import re

from kayan_knowledge import (
    CATALOG,
    CITY_SCENES,
    FAMILIES,
    family_of,
    overlay_for,
    related_services,
)
from oman_copy import CITIES
from publish_schedule_oman import PHONE, WHATSAPP

ARTICLE_VER = "kayan-v1"
WA = f"https://wa.me/{WHATSAPP}"
TEL = f"tel:{PHONE}"

CSS = """
<style>
.rukn-art{--navy:#0A1F4E;--teal:#1FB5A3;--blue:#2E9DF7;--line:#e3e9f2;--bg:#f9fcff;--text:#151c28;color:var(--text);line-height:1.85;font-size:1.05rem}
.rukn-art .article-hero{background:linear-gradient(135deg,var(--navy),#14335e);color:#fff;border-radius:16px;padding:22px 18px;margin:18px 0}
.rukn-art .hero-label{display:inline-block;background:rgba(46,157,247,.2);color:#d6e9ff;border-radius:999px;padding:4px 12px;font-size:.85rem;margin-bottom:8px}
.rukn-art .hero-buttons{display:flex;flex-wrap:wrap;gap:10px;margin-top:14px}
.rukn-art .cta-button{display:inline-flex;align-items:center;gap:8px;background:var(--blue);color:#fff;text-decoration:none;border-radius:12px;padding:12px 16px;min-height:44px}
.rukn-art .whatsapp-button{background:#1FB5A3}
.rukn-art .features-grid,.rukn-art .steps-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:16px 0}
.rukn-art .feature-card,.rukn-art .step-card{background:var(--bg);border:1px solid var(--line);border-radius:14px;padding:14px}
.rukn-art .step-number{display:inline-block;background:var(--navy);color:#fff;border-radius:8px;padding:2px 8px;font-size:.8rem;margin-bottom:6px}
.rukn-art .warning-box,.rukn-art .expert-tip{border-radius:14px;padding:14px 16px;margin:16px 0}
.rukn-art .warning-box{background:#fff6e8;border:1px solid #f0d2a0}
.rukn-art .expert-tip{background:#eefaf7;border:1px solid #bfe8df}
.rukn-art .cta-section{background:var(--navy);color:#fff;border-radius:16px;padding:20px 16px;margin:22px 0;text-align:center}
.rukn-art .cta-section h2{color:#fff}
.rukn-art .responsive-table{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:14px 0}
.rukn-art table{width:100%;border-collapse:collapse;min-width:280px}
.rukn-art th,.rukn-art td{border:1px solid var(--line);padding:10px;text-align:right;vertical-align:top}
.rukn-art th{background:var(--navy);color:#fff}
.rukn-art tr:nth-child(even) td{background:#f4f8fc}
@media(max-width:640px){.rukn-art .features-grid,.rukn-art .steps-grid{grid-template-columns:1fr}.rukn-art .hero-buttons{flex-direction:column}.rukn-art .cta-button{justify-content:center;width:100%}}
</style>
"""


def _rng(*parts: str) -> random.Random:
    seed = hashlib.sha256("|".join(parts).encode("utf-8")).digest()
    return random.Random(int.from_bytes(seed[:8], "big"))


def _pick(rng: random.Random, items: list, n: int) -> list:
    pool = list(items)
    rng.shuffle(pool)
    return pool if n >= len(pool) else pool[:n]


def _city(city: str) -> dict:
    return CITIES.get(city, CITIES["muscat"])


def _areas_list(city: str) -> list[str]:
    return [a.strip() for a in _city(city)["areas_ar"].split("،") if a.strip()]


def _kw(title: str, city_ar: str) -> str:
    t = title.strip()
    if city_ar and city_ar not in t:
        t = f"{t} في {city_ar}"
    return t


def _word_count(html: str) -> int:
    text = re.sub(r"<style.*?</style>", " ", html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\[post_[a-z_]+\]", " ", text)
    return len(re.findall(r"\S+", text))


def _ul(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>"


def _table(headers: list[str], rows: list[list[str]]) -> str:
    head = "<tr>" + "".join(f"<th>{h}</th>" for h in headers) + "</tr>"
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    return f'<div class="responsive-table"><table><thead>{head}</thead><tbody>{body}</tbody></table></div>'


def _icon(fam_icon: str) -> str:
    return f'<i class="fas {fam_icon}"></i>'


def build_article(title: str, slug: str, service: str, city: str) -> dict:
    c = _city(city)
    fam_id = family_of(service)
    fam = FAMILIES[fam_id]
    over = overlay_for(service)
    name = CATALOG.get(service, title)
    kw = _kw(title, c["ar"])
    rng = _rng(service, city, "rukn-oman-kayan-v1")
    rng_svc = _rng(service, "svc-core")
    areas = _areas_list(city)
    scenes = CITY_SCENES.get(city, CITY_SCENES["muscat"])
    scene_a, scene_b = rng.sample(scenes, 2) if len(scenes) >= 2 else (scenes[0], scenes[0])
    area_a, area_b, area_c = (areas + areas)[:3]
    related = related_services(service, 5)
    rng.shuffle(related)
    related = related[:4]

    signs = [
        f"{s} — نربط هذه العلامة بـ {name} في {c['ar']} لا بتشخيص عام."
        for s in _pick(rng, fam["signs"] + list(over.get("signs") or []), 6)
    ]
    causes = [
        f"{s} ويظهر أثره بوضوح مع {c['climate_ar']}."
        for s in _pick(rng, fam["causes"], min(5, len(fam["causes"])))
    ]
    types = list(fam["types"])
    rng_svc.shuffle(types)
    steps = list(fam["steps"])
    if rng.random() > 0.5:
        steps = steps[1:] + steps[:1]
    tools = [
        f"{s} إن كانت معاينة {name} تستدعيه، لا كعرض عدة للتسويق."
        for s in _pick(rng, fam["tools"] + list(over.get("tools") or []), 5)
    ]
    mistakes = [
        f"{s} وهذا يضر نتائج {name} أكثر مما يختصر الوقت."
        for s in _pick(rng, fam["mistakes"] + list(over.get("mistakes") or []), 4)
    ]
    cost = list(fam["cost"])
    rng.shuffle(cost)
    features = list(fam["features"])
    rng.shuffle(features)
    when = _pick(rng, fam["when"], min(4, len(fam["when"])))
    angle = over["angle"]

    intro_pool = [
        f"إذا لاحظت {fam['problem']} في {c['ar']} فالحل العملي يبدأ بمعاينة الميدان لا بتجربة عشوائية. {kw} من ركن التطور تعني {fam['what']} مع مراعاة {c['climate_ar']}.",
        f"{fam['problem']} لا يُعالَج من صورة واتساب وحدها. {kw} تعتمد على فحص الموقع داخل {c['gov_ar']} ثم عرض سعر بالريال العُماني.",
        f"السؤال الذي يصلنا من {area_a} و{area_b}: هل المشكلة ظاهرة أم مصدرها مخفي؟ {angle} هذا هو مدخل {kw}.",
        f"في {c['stock_ar']} تختلف طريقة العمل عن بيت بتصميم آخر. لذلك {kw} لا تُنسخ من مدينة ثانية حرفياً.",
        f"{c['note_ar']}. ومع ذلك يبقى المبدأ واحداً: {fam['what']} بعد معاينة، والتسعير بعد التشخيص.",
        f"أول 10 دقائق في الموقع توضح إن كانت الحالة {when[0]} أم شيئاً أعمق. بعدها يتحدد نطاق {name} في {c['ar']}.",
    ]
    intro = intro_pool[rng.randrange(len(intro_pool))]
    intro2 = (
        f"{scene_a} {angle} المناطق المعتادة للتنفيذ تشمل {c['areas_ar']} حسب الاتفاق. "
        f"لا نكتب أسعاراً ثابتة هنا لأن المساحة وحالة {fam['kw']} تتغير من بيت إلى بيت."
    )
    intro3 = (
        f"البحث عن {kw} يعني غالباً نية محلية تجارية: هل تُنفَّذ الخدمة في {c['ar']} وكيف تُشخَّص. "
        f"التفاصيل أدناه تخص {name} لا قالباً عاماً."
    )

    hero_h = rng.choice(
        [
            f"{fam['what']} في {c['ar']}",
            f"معاينة {fam['kw']} داخل {c['gov_ar']}",
            f"خطة عمل واضحة لـ {name}",
        ]
    )
    hero_p = rng.choice(
        [
            f"{angle} الفريق يزور الموقع في {c['ar']} ثم يكتب النطاق قبل التنفيذ.",
            f"نبدأ من المشكلة الظاهرة في {area_c} وصولاً إلى السبب، لا العكس.",
            f"{scene_b}",
        ]
    )

    related_html = "<ul>" + "".join(
        f'<li><a href="/om/{svc}-{city}/">{CATALOG.get(svc, svc)} في {c["ar"]}</a></li>'
        for svc in related
    ) + "</ul>"

    faq_all = _faqs(name, city, c, fam, angle, rng)
    faq_content = faq_all[:4]
    faq_box = faq_all[4:12]

    h_what = rng.choice(
        [f"ما الذي تعنيه {name} عملياً؟", f"تعريف {fam['kw']} كما يُنفَّذ في {c['ar']}", f"هل {name} مناسبة لحالتك؟"]
    )
    h_when = rng.choice(
        [f"متى تطلب {fam['kw']} في {c['ar']}؟", f"حالات تستدعي زيارة لـ {name}", "علامات أن التأجيل سيكلف أكثر"]
    )
    h_signs = rng.choice(["ما الذي تلاحظه قبل الزيارة؟", "أعراض تستحق التوثيق بالصور", f"قراءة المشكلة في بيوت {c['ar']}"])
    h_causes = rng.choice(["من أين تبدأ المشكلة؟", f"أسباب شائعة داخل {c['gov_ar']}", "ما الذي يُخطئ الناس في تفسيره؟"])
    h_types = rng.choice(["أنواع العمل حسب الحالة", f"كيف تُقسَّم {fam['kw']}؟", "نطاق ضيق أو مسار كامل"])
    h_how = rng.choice(["كيف تسير الزيارة؟", "تسلسل التنفيذ بعد الاتفاق", f"خطوات {name} بدون حشو"])
    h_tools = rng.choice(["أدوات تُستخدم عند الحاجة", "لماذا لا تكفي العدة المنزلية؟", "التقنية المناسبة لا الأغلى دائماً"])
    h_feat = rng.choice(["ماذا تتوقع من التنفيذ المنظم؟", "فوائد التشخيص قبل الإصلاح", "ما الذي يتغير بعد الزيارة الصحيحة؟"])
    h_err = rng.choice(["أخطاء تزيد الضرر", "ما الذي لا ننصح بتجربته", "ممارسات تبدو سريعة وتكلف لاحقاً"])
    h_cost = rng.choice(
        [f"كم تكلفة {fam['kw']} في {c['ar']}؟", "ما الذي يحرّك السعر بعد المعاينة؟", "لماذا لا يوجد رقم ثابت في هذه الصفحة؟"]
    )
    h_local = rng.choice(
        [f"العمل داخل {c['ar']} والمناطق المحيطة", f"{c['gov_ar']}: ظروف تؤثر على التنفيذ", "كيف تختلف الأحياء دون حشو أسماء"]
    )
    h_rel = rng.choice(["خدمات مرتبطة قد تحتاجها بعد التشخيص", "ماذا لو اكتشفنا مشكلة مجاورة؟", "روابط داخلية لصفحات منفصلة"])
    h_faq = rng.choice(["أسئلة يطرحها العملاء قبل الحجز", f"استفسارات {fam['kw']} بإجابات مباشرة", "إجابات قصيرة ثم التفاصيل في الأسفل"])
    h_end = rng.choice(["كيف تبدأ؟", "الخطوة التالية بعد قراءة الدليل", "طلب معاينة في مدينتك"])

    type_rows = [[t, f"يُختار إذا كانت المعاينة تشير إلى هذا المسار في {c['ar']}", "حسب الاتفاق"] for t in types]
    cmp_rows = [
        ["التشخيص", "معاينة وقياس حسب الحالة", "تجربة مادة أو تكسير مباشر"],
        ["الوضوح", "نطاق مكتوب قبل التنفيذ", "اتفاق شفهي يتوسع أثناء العمل"],
        ["المناخ المحلي", c["climate_ar"], "خطة منسوخة من مدينة أخرى"],
        ["التسعير", "ريال عُماني بعد الزيارة", "رقم هاتفي بلا فحص"],
    ]
    rng.shuffle(cmp_rows)
    cost_rows = [[item, "يؤثر على الوقت والخامات لا كرقم مخترع"] for item in cost]
    dur = rng.choice(["تُحدد بعد المعاينة", "زيارة واحدة أو أكثر حسب النطاق", "تُكتب في العرض"])
    svc_rows = [[name, fam["what"], "تقليل تكرار العطل", dur]]
    for svc in related[:3]:
        svc_rows.append(
            [
                CATALOG.get(svc, svc),
                FAMILIES[family_of(svc)]["what"],
                "تُطلب إن ظهرت حاجة أثناء الفحص",
                "مستقلة عن هذه الصفحة",
            ]
        )

    feature_cards = "".join(
        f'<div class="feature-card">{_icon(fam["icon"])}<h3>{t}</h3><p>{p}</p></div>' for t, p in features[:4]
    )
    step_cards = "".join(
        f'<div class="step-card"><span class="step-number">{i:02d}</span><h3>{s}</h3><p>تُنفَّذ هذه الخطوة في {c["ar"]} فقط إذا كانت الحالة تستدعيها بعد الفحص.</p></div>'
        for i, s in enumerate(steps, 1)
    )
    faq_html = "".join(f"<h3>{q}</h3><p>{a}</p>" for q, a in faq_content)

    para_local = (
        f"{scene_b} التغطية تشمل {c['areas_ar']} ضمن اتفاق الزيارة لا كقائمة تُحشر في كل جملة. "
        f"{c['note_ar']} طبيعة المباني: {c['stock_ar']}."
    )
    para_safety = rng.choice(
        [
            f"أي عمل يمس الكهرباء أو الغاز أو السطح يُنفَّذ بعد تأمين المنطقة وإبعاد الأطفال. في {c['ar']} الحرارة والغبار عاملان إضافيان على المعدات الخارجية.",
            f"لا نستخدم مواداً داخل المجلس دون توضيح إن كانت ذات رائحة أو تحتاج تهوية. خصوصية البيت العُماني جزء من ترتيب الدخول.",
            f"إذا تطلب العمل إغلاق ماء أو كهرباء نذكر المدة المتوقعة قبل البدء حتى ترتب الأسرة يومها في {area_b}.",
        ]
    )
    para_after = rng.choice(
        [
            f"بعد التسليم يبقى سبب المشكلة مكتوباً حتى لا تُعاد نفس التجربة بعد شهر. إن لزم قياس لاحق يُذكر في العرض.",
            f"الصيانة الوقائية تختلف عن الإصلاح الطارئ؛ لا نخلطهما في فاتورة واحدة دون بند واضح.",
            f"الصور قبل وبعد تُلتقط عند الحاجة لتوضيح المصدر لا للتسويق المبالغ فيه.",
        ]
    )
    para_intent = (
        f"نية البحث عن {kw} تجارية محلية: العميل يريد أن يعرف إن كانت الخدمة تُنفَّذ في {c['ar']}، "
        f"كيف تُشخَّص، وما الذي يحرّك السعر. الصفحة تجيب عن ذلك دون ادعاء ترتيب مضمون في نتائج البحث."
    )
    notes = _field_notes(rng, name, c, fam, angle, area_a, area_b, service)

    sec = {}
    sec["what"] = f"""<h2>{h_what}</h2>
<p>{fam['what']}. {angle}</p>
<p>{name} في {c['ar']} ليست وصفة واحدة لكل المباني. {c['stock_ar']}. لذلك نسأل عن عمر التمديدات وعدد المستخدمين وموقع العطل الظاهر قبل أن نفتح العدة. الزيارة تفرّق بين عَرَض تجميلي ومصدر يهدد الشبكة أو الخامة.</p>
<p>{para_intent}</p>
<p>{notes[0]}</p>
<p>{notes[1]}</p>"""
    sec["when"] = f"""<h2>{h_when}</h2>
<p>تحتاج الخدمة عندما يتكرر أحد هذه الأمور:</p>
{_ul(when)}
<p>إذا كانت الحالة طارئة نؤمّن أولاً ثم نحدد باقي النطاق. غير ذلك يمكن ترتيب موعد يناسب طبيعة الحركة في {c['ar']}.</p>"""
    sec["signs"] = f"""<h2>{h_signs}</h2>
<p>صوّر النقطة من زاويتين إن استطعت؛ ذلك يختصر وقت المعاينة في {area_a}.</p>
{_ul(signs)}
<p>{scene_a}</p>"""
    sec["causes"] = f"""<h2>{h_causes}</h2>
<p>السبب الظاهر قد يكون نتيجة لا أصلاً. في {c['gov_ar']} يتكرر:</p>
{_ul(causes)}
<p>{c['climate_ar']}. تجاهل هذا العامل يجعل نفس العطل يعود بعد أسابيع.</p>"""
    sec["types"] = f"""<h2>{h_types}</h2>
<p>لا يُنفَّذ كل نوع في كل زيارة. الجدول يوضح المسارات الشائعة بلا أسعار مخترعة.</p>
{_table(["المسار", "متى يُطرح", "المدة"], type_rows)}
<p>إن اكتُشف أثناء الفحص أن الحالة أقرب لخدمة أخرى نذكر ذلك بدل إكمال عمل غير مناسب.</p>"""
    sec["how"] = f"""<h2>{h_how}</h2>
<p>التسلسل التالي إطار عام؛ ترتيب البنود قد يختلف إذا كانت السلامة تتطلب تقديماً أو تأخيراً. في {c['ar']} نراعي حرارة الظهيرة على المعدات الخارجية ووقت دخول العمارات.</p>
<div class="steps-grid">{step_cards}</div>
[post_steps]
<p>قبل المغادرة نراجع معك ما أُنجز وما يحتاج زيارة لاحقة أو خامة غير متوفرة في السيارة. هذا الملخص يمنع سوء الفهم عندما يسأل أحد أفراد الأسرة لاحقاً عمّا تغيّر.</p>
<p>{notes[4]}</p>"""
    sec["tools"] = f"""<h2>{h_tools}</h2>
<p>الأدوات تُختار حسب العطل لا حسب ما يبدو أحدث. الشائع في {fam['kw']}:</p>
{_ul(tools)}
<blockquote class="expert-tip"><i class="fas fa-lightbulb"></i> <strong>نصيحة مهمة:</strong> {angle}</blockquote>"""
    sec["feat"] = f"""<h2>{h_feat}</h2>
<div class="features-grid">{feature_cards}</div>
[post_features]
<p>هذه طريقة عمل للنطاق المتفق عليه داخل {c['ar']} وليست وعداً عاماً لكل بيت.</p>"""
    sec["err"] = f"""<h2>{h_err}</h2>
<blockquote class="warning-box"><i class="fas fa-exclamation-triangle"></i> <strong>تنبيه:</strong> التجارب المنزلية العشوائية قد تخفي المصدر وتوسّع الضرر خصوصاً مع الرطوبة أو الكهرباء.</blockquote>
{_ul(mistakes)}
<p>{para_safety}</p>"""
    sec["cost"] = f"""<h2>{h_cost}</h2>
<p>لا نضع جدولاً بأرقام ريال مخترعة. السعر يُكتب بعد المعاينة حسب حالة {name} في هذا العقار تحديداً.</p>
{_table(["العامل", "لماذا يؤثر"], cost_rows)}
[post_prices]
<p>العرض بالريال العُماني. أي بند إضافي يُضاف كتابياً قبل تنفيذه. إن رفضت بنداً نوقف عنده ولا نكمل لأن العمل بدأ.</p>
<p>{notes[5]}</p>"""
    sec["local"] = f"""<h2>{h_local}</h2>
<p>{para_local}</p>
<p>مثال عملي: عمل في {area_a} قد يختلف عن {area_b} في سهولة الوقوف وارتفاع الخزان أو نوع الأرضية. لا نكرر اسم المدينة في كل سطر لأن المقصود ظروف الموقع لا حشو جغرافي.</p>
<p>{notes[2]}</p>
<p>{notes[3]}</p>
{_table(["الخدمة", "الوصف", "الفائدة", "المدة"], svc_rows)}"""
    sec["cmp"] = f"""<h2>{rng.choice(["مقارنة مسار منظم ومسار متعجل", "ماذا يتغير إذا اكتفيت بالترقيع؟", "حدود الحل المنزلي"])}</h2>
{_table(["المعيار", "بعد معاينة منظمة", "المسار المتعجل"], cmp_rows)}
<p>المقارنة توضح فرق المنهج لا هجوماً على شركات أخرى.</p>"""
    sec["after"] = f"""<h2>{rng.choice(["بعد انتهاء العمل", "كيف تقلل عودة المشكلة؟", "صيانة بسيطة بين الزيارات"])}</h2>
<p>{para_after}</p>
<p>{para_safety}</p>
<p>{notes[6]}</p>"""
    sec["ops"] = f"""<h2>{rng.choice([f"تشغيل {name} داخل {c['gov_ar']}", f"ما الذي يتغير من حي إلى حي في {c['ar']}؟", "ترتيب الزيارة على الأرض"])}</h2>
<p>{notes[7]}</p>
<p>{notes[8]}</p>
<p>{c['climate_ar']} لذلك جدول {fam['kw']} في {c['ar']} ليس نسخة من محافظة أخرى حتى لو تشابه اسم الخدمة. الفريق يخرج بعدة تناسب {c['stock_ar']} لا بعدة استعراض.</p>
<p>الوصول إلى {area_a} غير الوصول إلى {area_b}: الموقف، تصريح العمارة، وارتفاع الخزان يغيّرون زمن التجهيز قبل أن يبدأ عمل {name} فعلياً. نذكر ذلك في موعد الزيارة حتى لا يُفهم التأخير كتقصير.</p>
<p>إذا طُلب اختصار يخالف {angle} نوضّح العاقبة بدل التنفيذ الصامت. الصفحة لا تعد بأسرع أو أرخص خدمة في السلطنة؛ تعد بتشخيص مكتوب ونطاق واضح بالريال العُماني.</p>
<p>بعد الاتفاق يبقى التواصل على الرقم المنشور في الموقع. لا نطلب دفعاً إلى حسابات تُرسل في رسائل مجهولة، ولا نستخدم تقييمات مخترعة لإثبات الجودة.</p>"""
    sec["rel"] = f"""<h2>{h_rel}</h2>
<p>قد تكشف المعاينة حاجة مجاورة. الصفحات التالية منفصلة حتى لا تُخلط الخدمات:</p>
{related_html}
[post_services]
<p>يمكنك أيضاً مراجعة <a href="/om/our-services/">تصنيفات الخدمات</a> أو <a href="/om/city/{city}/">خدمات {c['ar']}</a>.</p>"""

    middle_keys = ["what", "when", "signs", "causes", "types", "how", "tools", "feat", "err", "cmp", "after", "local", "ops"]
    rng.shuffle(middle_keys)
    if "what" in middle_keys:
        middle_keys.remove("what")
        middle_keys.insert(rng.randint(0, 1), "what")

    hero = f"""<section class="article-hero"><div class="hero-content"><span class="hero-label">ركن التطور — {c['gov_ar']}</span>
<h2>{hero_h}</h2><p>{hero_p}</p>
<div class="hero-buttons"><a href="{TEL}" class="cta-button"><i class="fas fa-phone"></i> اتصل الآن</a>
<a href="{WA}" class="cta-button whatsapp-button" rel="noopener"><i class="fab fa-whatsapp"></i> واتساب</a></div></div></section>"""

    cta_mid = f"""<section class="cta-section"><i class="fas fa-headset"></i>
<h2>هل تحتاج إلى {name} في {c['ar']}؟</h2>
<p>صف العطل أو أرسل صورة، ونحدد إن كانت الزيارة في {c['ar']} كافية أم أن الحالة تحتاج تجهيزاً خاصاً.</p>
<a href="{TEL}" class="cta-button"><i class="fas fa-phone"></i> اتصل الآن</a></section>
[post_call]"""

    faq_sec = f"""<h2>{h_faq}</h2>
{faq_html}
<p>المزيد من الأسئلة في بلوك الأسئلة الشائعة أسفل المقال حتى تبقى الصفحة مقروءة على الهاتف.</p>"""

    end_sec = f"""<h2>{h_end}</h2>
<p>للتواصل: <a href="{TEL}">{PHONE}</a> أو واتساب عبر <a href="{WA}" rel="noopener">{PHONE}</a>. ساعات العمل المعتادة السبت–الخميس 08:00–21:00 بتوقيت مسقط، والطوارئ حسب توفر الفريق.</p>
<p>{kw} خدمة ميدانية داخل سلطنة عُمان. لا نربط التسعير بعملة دولة أخرى، ولا نعد بترتيب بحث لا نملكه.</p>
<p><a href="/om/contact/">صفحة اتصل بنا</a> · <a href="/om/cities/">المدن</a> · <a href="/om/faq/">الأسئلة العامة</a></p>
<!--rukn-pad-->"""

    chunks = [sec[k] for k in middle_keys]
    cut = max(3, len(chunks) // 2)
    body = "\n".join(chunks[:cut] + [cta_mid] + chunks[cut:] + [sec["rel"], sec["cost"], faq_sec, end_sec])
    html = f"""{CSS}
<div class="rukn-art">
<p class="rukn-oman-intro">{intro}</p>
<p>{intro2}</p>
<p>{intro3}</p>
{hero}
{body}
</div>
"""
    html = _pad_if_short(html, title, name, service, city, c, fam, angle, rng, related)

    excerpt = (
        f"{kw}: {angle} معاينة في {c['ar']} داخل {c['gov_ar']} ثم عرض بالريال العُماني. "
        f"تغطية حسب الاتفاق: {area_a} و{area_b}."
    )[:180]
    seo_title = f"{kw} | ركن التطور عُمان"
    seo_desc = excerpt[:160]
    focus = kw[:80]
    tags = _tags(name, service, city, c, fam)
    en = _english(name, service, city, c, angle, related)

    feature_items = [{"title": t, "content": p, "icon": f'<i class="fas {fam["icon"]}"></i>'} for t, p in features[:5]]
    step_items = [{"title": s, "content": f"تنفَّذ في {c['ar']} عند الحاجة بعد الفحص."} for s in steps]
    service_items = [{"title": CATALOG.get(s, s), "content": f"صفحة مستقلة داخل {c['ar']}.", "image": ""} for s in related]
    price_items = [{"title": row[0], "value": "يُحدد بعد المعاينة"} for row in cost_rows]

    meta = {
        "yourcolor__faqs": [{"question": q, "answer": a} for q, a in faq_box],
        "post__features__data": {
            "features__title": f"مميزات {name} في {c['ar']}",
            "features__content": angle,
            "yourcolor__post_features": feature_items,
        },
        "post__work_steps__data": {
            "work_steps__title": f"خطوات {fam['kw']}",
            "work_steps__content": f"الإطار العام لتنفيذ {name} بعد المعاينة في {c['ar']}.",
            "work_steps_items": step_items,
        },
        "post__services__data": {
            "services__title": f"خدمات مرتبطة في {c['ar']}",
            "services__content": "صفحات منفصلة حتى لا تُخلط الأعمال.",
            "post_services_items": service_items,
        },
        "post__price_list__data": {
            "price_list__title": "عوامل السعر لا أرقام مخترعة",
            "price_list__content": f"تكلفة {name} تُكتب بالريال العُماني بعد الزيارة في {c['ar']}.",
            "price_list__table_title1": "البند",
            "price_list__table_title2": "التقدير",
            "price_list__items": price_items,
        },
        "post__call_section__data": {
            "call_section_title": f"طلب {name} في {c['ar']}",
            "call_section_content": f"{angle} تواصل لتحديد المعاينة.",
            "call_section_phone": PHONE,
            "call_section_whatsapp": WHATSAPP,
        },
        "post__card__data": {
            "post_card_title": kw,
            "post_card_content": excerpt,
            "hide__card__callbutton": "",
            "hide__card__whatsapp": "",
        },
        "post__popover__data": {
            "popover_call_title": f"{name} في {c['ar']}",
            "popover_call_content": "صف المشكلة أو أرسل صورة لتحديد موعد المعاينة.",
            "popover_call_icon": f'<i class="fas {fam["icon"]}"></i>',
        },
        "post__service_request__data": {
            "orderservices": f"طلب {name}",
            "contentservices": f"معاينة في {c['gov_ar']} ثم عرض مكتوب بالريال العُماني.",
            "hide__service__callbutton": "",
            "hide__service__whatsapp": "",
        },
        "YourColor_Service": {
            "hide_schema_Service": "",
            "priceRange": "OMR",
            "description": seo_desc,
            "addressLocality": c["ar"],
            "postalCode": "",
            "telephone": PHONE,
            "addressCountry": "OM",
            "streetAddress": c["gov_ar"],
            "addressRegion": "سلطنة عُمان",
            "areaServed": c["areas_ar"],
            "identifier": slug,
            "additionalType": fam["kw"],
            "OfferCatalog": name,
        },
        "YourColor_Article": {
            "hide_schema_Article": "",
            "headline": kw,
            "description": seo_desc,
            "articleBody": excerpt,
        },
        "phone_number": PHONE,
        "whatsapp_number": WHATSAPP,
        "references": "",
        "hide_features__section": "",
        "hide_work_steps": "",
        "hide_services_section": "",
        "hide_price_list__section": "",
        "hide_call_section": "",
        "hide_post_gallery": "on",
        "hide__post_card": "",
        "rank_math_title": seo_title,
        "rank_math_description": seo_desc,
        "rank_math_focus_keyword": focus,
        "rank_math_canonical_url": f"https://rukn-eltatawer.com/om/{slug}/",
        "rank_math_robots": "index, follow",
        "rank_math_facebook_title": seo_title,
        "rank_math_facebook_description": seo_desc,
        "rank_math_twitter_title": seo_title,
        "rank_math_twitter_description": seo_desc,
        "_rukn_lang": "ar",
        "_rukn_pair_slug": slug,
        "_rukn_en_title": en["title"],
        "_rukn_en_content": en["html"],
        "_rukn_en_excerpt": en["desc"],
        "_rukn_en_desc": en["desc"],
        "_rukn_article_ver": ARTICLE_VER,
    }

    return {
        "content": html,
        "excerpt": excerpt,
        "tags": tags,
        "meta": meta,
        "seo_title": seo_title,
        "focus": focus,
        "words": _word_count(html),
        "h2": re.findall(r"<h2>(.*?)</h2>", html),
    }


def _field_notes(rng, name, c, fam, angle, area_a, area_b, service):
    pool = [
        f"في {area_a} نسأل أولاً عن مصدر المياه والكهرباء لأن ضعف الضغط أو فصل القاطع يغيّر تشخيص {name}. لا نبدأ بحل جاهز من زيارة سابقة في حي آخر.",
        f"بيوت {area_b} قد تختلف في ارتفاع الخزان أو ضيق الموقف. ذلك يؤثر على عدة {fam['kw']} وعلى مدة التجهيز قبل أول خطوة تنفيذ.",
        f"{c['climate_ar']}. تجاهل هذا العامل يجعل نتائج {name} قصيرة العمر حتى لو بدا الشكل النهائي مقبولاً يوم التسليم.",
        f"{c['stock_ar']}. لذلك نوثق نوع الأرضية والسطح الظاهر قبل اختيار مادة قد تخدش أو لا تلتصق.",
        f"{c['note_ar']} مواعيد {fam['kw']} تُؤكد صباح التنفيذ إذا كان الطريق أو الزحام عاملًا، لا قبلها بأسبوع كوعد جامد.",
        f"{angle} هذه الجملة ليست شعاراً؛ هي معيار نرجع إليه إذا طُلب منا اختصار يخالف التشخيص.",
        f"إن كان العقار مؤجراً في {c['ar']} نفصل بين وصف المستأجر للعَرَض وقرار المالك في التكسير أو الاستبدال، حتى لا يُنفَّذ بند بلا صلاحية.",
        f"الصيف يطيل تشغيل الأجهزة في {c['gov_ar']}؛ ارتفاع الطلب لا يعني أن كل بلاغ {service.replace('-', ' ')} طارئ يستدعي كسراً فورياً.",
        f"لا نخلط {name} بخدمة مجاورة في نفس الفاتورة دون بند. الوضوح يحمي العميل من مفاجأة، ويحمي الصفحة من محتوى مكرر لخدمة أخرى.",
        f"الغبار والملوحة ليسا عذراً لتأخير العمل؛ هما سبب لترتيب المواد وطريقة التنظيف أو العزل بما يناسب {c['ar']} تحديداً.",
        f"إذا ظهرت حاجة لقطعة غير موجودة في السيارة نتوقف ونخبرك بدل تركيب بديل صامت. {name} تُقاس بالقرار الصحيح لا بسرعة المغادرة.",
        f"التصوير للنقطة المعنية يساعد أكثر من وصف طويل عبر الهاتف، خصوصاً عندما تكون البقعة في سقف {area_a} أو زاوية لا تظهر في الإضاءة المسائية.",
    ]
    rng.shuffle(pool)
    return pool


def _pad_if_short(html, title, name, service, city, c, fam, angle, rng, related):
    if _word_count(html) >= 2500:
        return html
    rel0 = CATALOG.get(related[0], fam["kw"]) if related else fam["kw"]
    extra_bits = [
        f"<h2>سياق إضافي لتنفيذ {name} في {c['ar']}</h2>",
        f"<p>{c['climate_ar']}. {c['stock_ar']}. {angle} عند العمل في {c['areas_ar']} نرتب الوقوف والعدة حسب عرض الشارع وارتفاع الخزان إن وُجد، ونفصل نطاق {name} عن أي بند لم يُذكر في العرض.</p>",
        f"<p>الفرق بين زيارة {rel0} وبين هذه الصفحة أن النطاق هنا هو {name} فقط. خلط الصفحات يضعف وضوح العرض للعميل كما يضعف تمييز الموضوع لمحرك البحث.</p>",
        f"<p>في الصيف العُماني يزداد الطلب على {fam['kw']} لأن الأجهزة والشبكات تعمل ساعات أطول. المعاينة في {c['ar']} تفرّق بين صوت مزعج وخطر حقيقي يستدعي تأميناً فورياً.</p>",
        f"<p>المواد تُذكر في العرض باسمها الشائع. إذا لم تتوفر خامة معينة نخبرك قبل البدء. لا نقدّم سرعة التسليم على ملاءمة الخامة لمناخ {c['gov_ar']}.</p>",
        f"<p>للعائلات نراعي أوقات المجلس والضيافة قدر الإمكان. الأعمال ذات الصوت أو الغبار أوضح صباحاً، والأعمال الداخلية المحدودة قد تناسب المساء إذا سمح الجدول.</p>",
        f"<p>لا نستخدم تقييمات أو أرقاماً غير موثقة في هذه الصفحة. المقياس العملي هو وضوح التشخيص والالتزام بالنطاق المكتوب بعد زيارة {title}.</p>",
        f"<p>الملخص الإنجليزي عبر /om/en/{service}-{city}/ موجّه للزائر غير العربي. المرجع التفصيلي لهذه الخدمة هو النص العربي في هذه الصفحة.</p>",
    ]
    extra = []
    probe = html
    for block in extra_bits:
        if _word_count(probe + "".join(extra)) >= 2500:
            break
        extra.append(block)
    return html.replace("<!--rukn-pad-->", "".join(extra) + "<!--rukn-pad-->", 1)


def _faqs(name, city, c, fam, angle, rng):
    first_area = c["areas_ar"].split("،")[0].strip()
    pairs = [
        (f"ما هي {name}؟", f"{fam['what']}. {angle}"),
        (f"هل تنفّذون {fam['kw']} في {c['ar']}؟", f"نعم داخل {c['gov_ar']} وحسب الاتفاق في {c['areas_ar']}."),
        ("هل يوجد سعر ثابت في الصفحة؟", "لا. السعر يُكتب بعد المعاينة بالريال العُماني حسب النطاق."),
        ("كم تستغرق الزيارة؟", "تُحدد بعد وصف الحالة وموقع العقار؛ المدة تُذكر في العرض لا كرقم عام لكل البيوت."),
        ("هل المعاينة ضرورية؟", "للأعمال التي تمس شبكات أو خامات أو ارتفاعات نعم. بعض الاستفسارات العامة تُجاب هاتفياً دون تسعير."),
        ("هل تعملون في عطلة نهاية الأسبوع؟", f"الجدول في {c['ar']} يعتمد على توفر الفريق."),
        ("ماذا أحضّر قبل وصول الفريق؟", "صور العطل، إتاحة الوصول للنقطة، وإبعاد ما يمنع الفحص في الغرفة المعنية."),
        ("هل تستخدمون مواداً ذات رائحة؟", "إن لزم نوضح ذلك مسبقاً ونرتب التهوية. لا نرش مادة غير متفق عليها في المجلس."),
        (f"هل {name} تشمل قطع الغيار؟", "القطعة بند مستقل إن احتيجت. تُذكر في العرض قبل التركيب."),
        ("كيف أدفع؟", "تفاصيل الدفع تُوضح عند الاتفاق. لا نطلب تحويلات إلى حسابات مجهولة عبر الرسائل."),
        ("ما الفرق بين هذه الصفحة وصفحة مدينة أخرى؟", f"الظروف في {c['ar']} تختلف؛ المحتوى مبني على {c['climate_ar']} و{c['stock_ar']}."),
        ("هل الضمان يشمل كل شيء؟", "الضمان إن وُجد يُذكر كتابياً حسب الخامة والعمل، وليس عبارة عامة في المقال."),
        ("هل تكسرون الأرضيات دائماً؟", "لا. التكسير قرار بعد تحديد المصدر إن كانت الخدمة من نوع الكشف أو الإصلاح المخفي."),
        (f"هل تغطون {first_area}؟", f"نعم ضمن تغطية {c['ar']} حسب موعد الفريق والمسافة داخل {c['gov_ar']}."),
        ("هل يوجد مهندس أم فني؟", "الزيارة ينفذها فني مختص بالحالة. الاستعانة بتخصص إضافي تُذكر إن ظهرت حاجة."),
        ("كيف أتابع العمل؟", "نقطة تواصل واحدة عبر الهاتف أو واتساب المسجّل في الموقع، مع ملخص ما نُفّذ."),
    ]
    rng.shuffle(pairs)
    return pairs


def _tags(name, service, city, c, fam):
    bits = [
        c["ar"],
        fam["kw"],
        name.replace("شركة ", "").replace("فني ", "")[:40],
        "سلطنة عُمان",
        c["gov_ar"],
        service.replace("-", " "),
    ]
    out = []
    for b in bits:
        b = re.sub(r"\s+", " ", b).strip()
        if b and b not in out:
            out.append(b)
    return out[:8]


def _english(name, service, city, c, angle, related):
    en_title = f"{name} in {c['en']}, Oman"
    rel = ", ".join(related[:3])
    html = f"""<section>
<h2>{en_title}</h2>
<p>Rukn Eltatawer provides this service in {c['en']} ({c['gov_en']}). {c['note_en']}. Local conditions: {c['climate_en']}. Building stock: {c['stock_en']}.</p>
<p>{angle}</p>
<p>We visit the property first, then issue a written quote in Omani rial. Neighbourhoods commonly covered by agreement: {c['areas_en']}.</p>
<p>Related Arabic pages on this site include {rel} in {c['en']}. This English block is a summary; the Arabic article is the full guide.</p>
<p>Contact: {PHONE} or WhatsApp {PHONE}. Arabic URL: /om/{service}-{city}/</p>
</section>"""
    desc = f"{name} in {c['en']}, Oman. Site visit then an OMR quote. {c['climate_en'][:80]}"[:160]
    return {"title": en_title, "html": html, "desc": desc}


if __name__ == "__main__":
    from publish_schedule_oman import split_slug

    samples = [
        "water-leak-detection-muscat",
        "water-leak-detection-salalah",
        "home-cleaning-muscat",
        "termite-control-nizwa",
    ]
    for slug in samples:
        svc, city = split_slug(slug)
        title = CATALOG.get(svc, svc) + f" في {_city(city)['ar']}"
        art = build_article(title, slug, svc, city)
        print(slug, "words", art["words"], "h2", len(art["h2"]))
        print(" ", art["h2"][:5])
