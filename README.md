# ركن التطور — عُمان

سكربت استيراد محتوى موقع [rukn-eltatawer.com/om](https://www.rukn-eltatawer.com/om) من ملف CSV.

## ماذا يفعل الاستيراد؟

- إنشاء 8 مدن (تصنيف `cities`): مسقط، صلالة، نزوى، صحار، صور، البريمي، عبري، الرستاق
- إنشاء 16 خدمة (نوع `services`) مع تصنيفاتها
- استيراد مقالات خدمات التنظيف من CSV (حوالي 168 مقالة بعد ترميم الصفوف الناقصة)
- استبدال `{PHONE_RUKN_OMAN}` و `{WHATSAPP_RUKN_OMAN}` برقم واتساب الموقع
- رفع صور غلاف بديلة لأن ملفات `service-*.webp` غير مرفقة مع CSV
- حذف مقالة Hello world الافتراضية

## التشغيل

لا تضع كلمة المرور في Git. استخدم كلمة مرور التطبيقات في ووردبريس:

```bash
export WP_USER='mahmoud'
export WP_APP_PASSWORD='xxxx xxxx xxxx xxxx xxxx xxxx'
python3 scripts/import_oman_wordpress.py --csv rukn-eltatawer-oman-FULL.csv.oplusdownload --status publish
```

اختياري: `WP_PHONE` و `WP_WHATSAPP` و `WP_BASE`.

السكربت يعيد استخدام العناصر الموجودة حسب الـ slug، فيمكن تشغيله مرة ثانية بأمان.

## تصحيح المحتوى وSEO (عربي + إنجليزي)

بعد الاستيراد:

```bash
export WP_USER='mahmoud'
export WP_APP_PASSWORD='xxxx xxxx xxxx xxxx xxxx xxxx'
export WP_ADMIN_PASSWORD='…'   # لرفع إضافة rukn-oman-seo فقط
python3 scripts/seo_fix_oman.py
```

السكربت يقوم بـ:

- رفع وتفعيل إضافة `plugins/rukn-oman-seo` (عناوين فريدة، canonical، hreflang، schema، `robots.txt`، `sitemap.xml`، ومسار `/en/`)
- حقن فقرة محلية عُمانية لكل مقالة مدينة حتى لا تبقى نسخاً متطابقة
- نسخة إنجليزية لكل مقالة تنظيف عبر `/om/en/{slug}/`
- ضبط اسم الموقع والمنطقة الزمنية `Asia/Muscat` واسم المؤلف
- تعطيل Polylang غير المكتمل حتى لا يكرر الصفحة الرئيسية على `/en/`

## ما تم ضبطه على الموقع الحي

- أرقام الاتصال/واتساب في إعدادات القالب: `+971586634710` / `971586634710`
- الروابط الدائمة للمقالات: `/%postname%/` (مثال: `/om/home-cleaning-muscat/`)
- عدّادات الصفحة الرئيسية: 16 خدمة، 8 مدن، 250+ مشروع، 2026 في عُمان منذ
- سؤال «كيف أطلب الخدمة؟» يعرض رقم الواتساب بدل النص الناقص
