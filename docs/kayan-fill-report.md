# Kayan field fill report

- time: 2026-09-22T02:44:21Z
- provider: none (empty-only classify; no LLM writes)
- mode: kayan
- apply: False
- mapping: post 1204 confirmed keys (`post__features__data`, `post__work_steps__data`, `post__price_list__data`, `post__services__data`, `post__call_section__data`)

- إجمالي المقالات: 1648
- تم تحديثه: 0
- تم تخطيه: 1648
- فشل: 0

## أهم الأخطاء

- لا توجد أخطاء تشغيل.
- كل المقالات الـ 1648 تم تخطيها بـ `--empty-only` لأن الشورت كودز `[post_*]` تتوسع في الواجهة والحقول غير فارغة.
- عينة من المحرر (1204، 1228، 450، 5108): `features__title` و`yourcolor__post_features[0][title]` مملوءة، السعر `يُحدد بعد المعاينة`، واتساب `971586634710`.
- لم يُستخدم `--force` ولم تُغيَّر المقالات أو الروابط.

## ملاحظات

Dry-run على خمسة مؤهلة لم يُنفَّذ لأن قائمة المؤهلين فارغة. `--apply --empty-only` على الكل يعطي نفس النتيجة: 0 تحديث.
