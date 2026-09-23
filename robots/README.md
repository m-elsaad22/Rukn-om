# robots.txt لكل دول ركن التطور

جوجل يقرأ ملفاً واحداً للنطاق: `https://rukn-eltatawer.com/robots.txt`

## أين تعدّل؟

لوحة **موقع الإمارات** (الجذر)، ليس لوحة عُمان:

1. Rank Math → إعدادات عامة → Edit robots.txt  
   أو ملف `robots.txt` بجانب `wp-config.php` في جذر الاستضافة.
2. الصق محتوى `root-robots.recommended.txt` أو أضف أسطر Sitemap الناقصة فقط.
3. إن وُجد ملف على www وآخر بدون www، ضع نفس المحتوى في الاثنين.
4. افتح بعدها: https://rukn-eltatawer.com/robots.txt

## السايتمابات التي تعمل الآن

| الدولة | المسار | السايتماب |
|---|---|---|
| الإمارات | `/` | `https://www.rukn-eltatawer.com/sitemap_index.xml` |
| السعودية | `/sa/` | `https://www.rukn-eltatawer.com/sa/sitemap_index.xml` |
| قطر | `/qa/` | `https://www.rukn-eltatawer.com/qa/sitemap_index.xml` |
| الكويت | `/kw/` | `https://rukn-eltatawer.com/kw/sitemap_index.xml` |
| عُمان | `/om/` | `https://rukn-eltatawer.com/om/sitemap.xml` |
| البحرين | `/bh/` | لا يوجد سايتماب بعد — فعّله من لوحة البحرين ثم أزل `#` في الملف |
| مصر | `/eg/` | لا يوجد سايتماب بعد — فعّله من لوحة مصر ثم أزل `#` في الملف |

في Search Console أضف خاصية لكل مسار (`/om/` و `/sa/` و `/qa/` و `/kw/` …) ثم أرسل سايتماب ذلك المسار.
