# فحص جودة مقالات موقع عُمان

المصدر: المقالات المنشورة حالياً على `https://rukn-eltatawer.com/om` عبر ووردبريس REST.
تاريخ الفحص: 4 أكتوبر 2026. المقالات المفحوصة: **1648**. الصفحات وأنواع الخدمات: **25**.

## إجابات الفحص

1. **أقل من 1000 كلمة:** لا توجد مقالة خدمة تحت 1000 كلمة (الوسيط 2701 كلمة). النقص في **24** صفحة محور/خدمة كيان بـ 43–284 كلمة فقط.
2. **نفس القالب:** **1648** مقالة من 1648 مبنية على قالب كيان واحد (عناوين ثابتة ونسبة جمل مكررة ≥ 35%).
3. **متشابهة:** **282** مقالة داخل **254** زوج شبه مكرر؛ منها 123 نسخة مدينة و131 تشابه بين خدمتين.
4. **لا تناسب الموضوع/الخدمة:** **186** مقالة، أغلبها خدمات شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة شمسية خارج نطاق الصفحة الرئيسية.
5. **أخطاء ونواقص:** كل المقالات تحمل نموذج هاتف إماراتي `05xxxxxxxx`. كذلك صورة بارزة مكررة، وعبارة «تغطية حسب الاتفاق:» بلا تكملة في 1244 مقالة.

## الخلاصة

| البند | العدد |
| --- | --- |
| مقالات منشورة | 1648 |
| وسيط عدد الكلمات | 2701 (من 2360 إلى 3040) |
| أقل من 1000 كلمة (مقالات) | 0 |
| أقل من 1000 كلمة (صفحات/خدمات كيان) | 24 |
| مكتوبة بنفس القالب | 1648 |
| متشابهة / شبه مكررة | 282 |
| لا تناسب الموضوع أو الخدمة | 186 |
| أخطاء أو نواقص | 1648 |
| أزواج شبه مكررة | 254 |
| خدمات خارج نطاق الموقع المعلن | 184 |

### كيف حُسبت النتائج

- **الكلمات**: الرموز بعد حذف HTML، مفصولة بمسافات. هذا مقياس «أقل من 1000 كلمة» كما يظهر للزائر.
- **نفس القالب**: تسلسل عناوين H2 بعد استبدال اسم المدينة/الخدمة، أو نسبة جمل القالب ≥ 35%.
- **التشابه**: simhash 64-بت بعد حذف أسماء المدن. Hamming ≤ 8 يعني شبه تطابق.
- **عدم التناسب**: مدينة العنوان ≠ الرابط، غياب كلمات الخدمة، سيطرة موضوع خدمة أخرى، أو خدمة خارج نطاق الصفحة الرئيسية.
- **النواقص**: شورت كود ظاهر، بقايا إمارات، عبارة ناقصة، تصنيف مفقود، صورة مكررة، فقرات متطابقة.

## 1) المقالات أقل من 1000 كلمة

لا توجد مقالة خدمة منشورة تحت 1000 كلمة. الوسيط حوالي ألفي كلمة لأن مولّد كيان يملأ قالباً طويلاً.

_لا توجد نتائج في هذه الفئة._

صفحات المحاور وخدمات كيان القصيرة (ليست مقالات):

| العنوان | الرابط | كلمات | كلمات فريدة | المدينة | الملاحظة |
| --- | --- | --- | --- | --- | --- |
| الصبغ والدهانات | https://www.rukn-eltatawer.com/om/services/painting/ | 43 | 43 |  | عدد الكلمات 43 أقل من 1000. |
| تنسيق الحدائق | https://www.rukn-eltatawer.com/om/services/landscaping/ | 43 | 43 |  | عدد الكلمات 43 أقل من 1000. |
| مكافحة الحشرات | https://www.rukn-eltatawer.com/om/services/pest-control/ | 43 | 43 |  | عدد الكلمات 43 أقل من 1000. |
| التنظيف والتعقيم | https://www.rukn-eltatawer.com/om/services/cleaning-sterilization/ | 43 | 43 |  | عدد الكلمات 43 أقل من 1000. |
| أعمال الكهرباء | https://www.rukn-eltatawer.com/om/services/electrical-works/ | 43 | 43 |  | عدد الكلمات 43 أقل من 1000. |
| تسليك المجاري | https://www.rukn-eltatawer.com/om/services/sewer-clearing/ | 43 | 43 |  | عدد الكلمات 43 أقل من 1000. |
| أعمال السباكة | https://www.rukn-eltatawer.com/om/services/plumbing/ | 43 | 43 |  | عدد الكلمات 43 أقل من 1000. |
| صيانة المباني | https://www.rukn-eltatawer.com/om/services/building-maintenance/ | 43 | 43 |  | عدد الكلمات 43 أقل من 1000. |
| الصيانة العامة | https://www.rukn-eltatawer.com/om/services/general-maintenance/ | 43 | 43 |  | عدد الكلمات 43 أقل من 1000. |
| عزل الأسطح | https://www.rukn-eltatawer.com/om/services/roof-insulation/ | 43 | 43 |  | عدد الكلمات 43 أقل من 1000. |
| تصميم وتنفيذ الديكورات | https://www.rukn-eltatawer.com/om/services/interior-design/ | 44 | 44 |  | عدد الكلمات 44 أقل من 1000. |
| تركيب الجبس بورد | https://www.rukn-eltatawer.com/om/services/gypsum-board/ | 44 | 44 |  | عدد الكلمات 44 أقل من 1000. |
| إنشاء وصيانة المسابح | https://www.rukn-eltatawer.com/om/services/swimming-pools/ | 44 | 44 |  | عدد الكلمات 44 أقل من 1000. |
| تركيب وصيانة التكييف | https://www.rukn-eltatawer.com/om/services/ac-install-maintenance/ | 44 | 44 |  | عدد الكلمات 44 أقل من 1000. |
| العزل المائي والحراري | https://www.rukn-eltatawer.com/om/services/thermal-waterproof-insulation/ | 44 | 44 |  | عدد الكلمات 44 أقل من 1000. |
| كشف تسربات المياه | https://www.rukn-eltatawer.com/om/services/water-leak-detection/ | 44 | 44 |  | عدد الكلمات 44 أقل من 1000. |
| الشروط والأحكام | https://www.rukn-eltatawer.com/om/terms/ | 73 | 73 |  | عدد الكلمات 73 أقل من 1000. |
| المدن | https://www.rukn-eltatawer.com/om/cities/ | 75 | 75 |  | عدد الكلمات 75 أقل من 1000. |
| اتصل بنا | https://www.rukn-eltatawer.com/om/contact/ | 91 | 91 |  | عدد الكلمات 91 أقل من 1000. |
| سياسة الخصوصية | https://www.rukn-eltatawer.com/om/privacy-policy/ | 92 | 92 |  | عدد الكلمات 92 أقل من 1000. |
| الأسئلة الشائعة | https://www.rukn-eltatawer.com/om/faq/ | 93 | 93 |  | عدد الكلمات 93 أقل من 1000. |
| من نحن | https://www.rukn-eltatawer.com/om/about/ | 94 | 94 |  | عدد الكلمات 94 أقل من 1000. استخدام «إمارة» في سياق عُمان. |
| خدماتنا | https://www.rukn-eltatawer.com/om/our-services/ | 109 | 109 |  | عدد الكلمات 109 أقل من 1000. |
| Rukn Eltatawer Oman / Cleaning and home services | https://www.rukn-eltatawer.com/om/en-home/ | 284 | 284 |  | عدد الكلمات 284 أقل من 1000. |

## 2) المقالات المكتوبة بنفس القالب

أكبر عائلات هيكل H2:

| بصمة الهيكل | عدد المقالات |
| --- | --- |
| `0b3d9377778c` | 1648 |

هذا هو الخطر الأكبر: **1648** مقالة تشارك هيكل كيان نفسه (أكبر عائلة: 1648 مقالة بنفس تسلسل العناوين). العناوين الثابتة تتكرر: عوامل السعر لا أرقام مخترعة، هل تحتاج إلى شركة، مناسبة لحالتك، الترقيع، التأجيل سيكلف، كيف تختلف الأحياء. الطول كبير، لكن التميّز ضعيف، والمدن الثماني لنفس الخدمة تبدو مقالاً واحداً مع استبدال اسم المدينة.

| العنوان | الرابط | كلمات | كلمات فريدة | المدينة | الملاحظة |
| --- | --- | --- | --- | --- | --- |
| شركة ترميم وصيانة مباني في عبري | https://www.rukn-eltatawer.com/om/building-renovation-ibri/ | 2611 | 1180 | ibri | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 55%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة تصميم حدائق داخلية في البريمي | https://www.rukn-eltatawer.com/om/indoor-garden-design-al-buraimi/ | 2619 | 1240 | al-buraimi | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 53%. تشابه مرتفع (hamming=7, cross-service-duplicate) مع https://www.rukn-eltatawer.com/om/... |
| شركة تنظيف سجاد في نزوى | https://www.rukn-eltatawer.com/om/carpet-cleaning-nizwa/ | 2684 | 1271 | nizwa | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 53%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة دهان شقق في صور | https://www.rukn-eltatawer.com/om/apartment-painting-sur/ | 2649 | 1260 | sur | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 52%. تشابه مرتفع (hamming=8, city-variant-template) مع https://www.rukn-eltatawer.com/om/ap... |
| شركة تركيب بلاستر في الرستاق | https://www.rukn-eltatawer.com/om/plastering-rustaq/ | 2646 | 1263 | rustaq | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 52%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة تركيب عرائش خشبية في البريمي | https://www.rukn-eltatawer.com/om/wooden-arbor-installation-al-buraimi/ | 2643 | 1263 | al-buraimi | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 52%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة تركيب ورق حائط في عبري | https://www.rukn-eltatawer.com/om/wallpaper-installation-ibri/ | 2675 | 1278 | ibri | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 52%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة قص عشب طبيعي في مسقط | https://www.rukn-eltatawer.com/om/natural-grass-cutting-muscat/ | 2788 | 1341 | muscat | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 52%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة تنظيف محلات تجارية ومولات في البريمي | https://www.rukn-eltatawer.com/om/mall-cleaning-al-buraimi/ | 2738 | 1338 | al-buraimi | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 51%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. |
| شركة تصميم حدائق أسطح في صور | https://www.rukn-eltatawer.com/om/roof-garden-design-sur/ | 2649 | 1295 | sur | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 51%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة تصميم وتنفيذ ديكورات في عبري | https://www.rukn-eltatawer.com/om/decor-design-ibri/ | 2674 | 1313 | ibri | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 51%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. صورة بارزة مكررة على... |
| شركة تنظيف مستشفيات وعيادات في الرستاق | https://www.rukn-eltatawer.com/om/hospital-clinic-cleaning-rustaq/ | 2698 | 1327 | rustaq | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 51%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة تنسيق حدائق في صلالة | https://www.rukn-eltatawer.com/om/landscaping-salalah/ | 2643 | 1306 | salalah | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 51%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة تركيب عرائش خشبية في عبري | https://www.rukn-eltatawer.com/om/wooden-arbor-installation-ibri/ | 2667 | 1320 | ibri | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 50%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة تنظيف واجهات زجاجية في صحار | https://www.rukn-eltatawer.com/om/glass-facade-cleaning-sohar/ | 2709 | 1343 | sohar | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 50%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة تنظيف مكاتب في عبري | https://www.rukn-eltatawer.com/om/office-cleaning-ibri/ | 2660 | 1322 | ibri | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 50%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة التعقيم بالبخار في صلالة | https://www.rukn-eltatawer.com/om/steam-disinfection-salalah/ | 2690 | 1340 | salalah | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 50%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة دهان بويات عالية الجودة في صحار | https://www.rukn-eltatawer.com/om/premium-paint-finishing-sohar/ | 2728 | 1360 | sohar | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 50%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. صورة بارزة مكررة على... |
| شركة تركيب نوافير جدارية في صحار | https://www.rukn-eltatawer.com/om/wall-fountain-sohar/ | 2690 | 1344 | sohar | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 50%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. صورة بارزة مكررة على... |
| شركة تنظيف واجهات زجاجية في صور | https://www.rukn-eltatawer.com/om/glass-facade-cleaning-sur/ | 2685 | 1345 | sur | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 50%. تشابه مرتفع (hamming=8, cross-service-duplicate) مع https://www.rukn-eltatawer.com/om/... |
| شركة تنظيف مطابخ في البريمي | https://www.rukn-eltatawer.com/om/kitchen-cleaning-al-buraimi/ | 2663 | 1334 | al-buraimi | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 50%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. |
| شركة تنظيف وتزيين الحدائق في البريمي | https://www.rukn-eltatawer.com/om/garden-cleaning-al-buraimi/ | 2670 | 1347 | al-buraimi | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 50%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة إنشاء ممرات حجرية في الرستاق | https://www.rukn-eltatawer.com/om/stone-pathway-rustaq/ | 2690 | 1355 | rustaq | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 50%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة تنظيف منازل في الرستاق | https://www.rukn-eltatawer.com/om/home-cleaning-rustaq/ | 2699 | 1361 | rustaq | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 50%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة التعقيم بالأوزون في نزوى | https://www.rukn-eltatawer.com/om/ozone-disinfection-nizwa/ | 2693 | 1360 | nizwa | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 50%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |

_1623 صفاً إضافياً في ملف CSV._

## 3) المقالات المتشابهة

أزواج شبه مكررة: **254** — منها 123 نسخة مدينة لنفس الخدمة، و131 تشابه بين خدمتين مختلفتين.

### تشابه بين خدمتين مختلفتين (أعلى خطورة)

| النوع | المسافة | عنوان أ | رابط أ | عنوان ب | رابط ب |
| --- | --- | --- | --- | --- | --- |
| cross-service-duplicate | 2 | شركة عزل خزانات في عبري | https://www.rukn-eltatawer.com/om/tank-insulation-ibri/ | شركة عزل مطابخ في عبري | https://www.rukn-eltatawer.com/om/kitchen-insulation-ibri/ |
| cross-service-duplicate | 4 | شركة صيانة نشافات في الرستاق | https://www.rukn-eltatawer.com/om/dryer-maintenance-rustaq/ | شركة صيانة غسالات في عبري | https://www.rukn-eltatawer.com/om/washer-maintenance-ibri/ |
| cross-service-duplicate | 4 | شركة كهربائي منازل في نزوى | https://www.rukn-eltatawer.com/om/home-electrician-elec-nizwa/ | كهربائي منازل في نزوى | https://www.rukn-eltatawer.com/om/home-electrician-nizwa/ |
| cross-service-duplicate | 4 | شركة عزل خزانات في نزوى | https://www.rukn-eltatawer.com/om/tank-insulation-nizwa/ | شركة عزل مطابخ في عبري | https://www.rukn-eltatawer.com/om/kitchen-insulation-ibri/ |
| cross-service-duplicate | 4 | شركة عزل ودهان أسطح في نزوى | https://www.rukn-eltatawer.com/om/roof-insulation-painting-nizwa/ | شركة عزل أسطح في عبري | https://www.rukn-eltatawer.com/om/roof-insulation-ibri/ |
| cross-service-duplicate | 4 | شركة عزل ودهان أسطح في مسقط | https://www.rukn-eltatawer.com/om/roof-insulation-painting-muscat/ | شركة عزل أسطح في مسقط | https://www.rukn-eltatawer.com/om/roof-insulation-muscat/ |
| cross-service-duplicate | 4 | شركة عزل صوتي في صور | https://www.rukn-eltatawer.com/om/soundproofing-sur/ | شركة عزل حراري في نزوى | https://www.rukn-eltatawer.com/om/thermal-insulation-nizwa/ |
| cross-service-duplicate | 4 | شركة عزل صوتي في نزوى | https://www.rukn-eltatawer.com/om/soundproofing-nizwa/ | شركة عزل حراري في صحار | https://www.rukn-eltatawer.com/om/thermal-insulation-sohar/ |
| cross-service-duplicate | 5 | شركة عزل خزانات في البريمي | https://www.rukn-eltatawer.com/om/tank-insulation-al-buraimi/ | شركة عزل مطابخ في عبري | https://www.rukn-eltatawer.com/om/kitchen-insulation-ibri/ |
| cross-service-duplicate | 5 | شركة عزل صوتي في صحار | https://www.rukn-eltatawer.com/om/soundproofing-sohar/ | شركة عزل خزانات في صحار | https://www.rukn-eltatawer.com/om/tank-insulation-sohar/ |
| cross-service-duplicate | 5 | شركة عزل ودهان أسطح في عبري | https://www.rukn-eltatawer.com/om/roof-insulation-painting-ibri/ | شركة عزل أسطح في عبري | https://www.rukn-eltatawer.com/om/roof-insulation-ibri/ |
| cross-service-duplicate | 5 | شركة عزل ودهان أسطح في نزوى | https://www.rukn-eltatawer.com/om/roof-insulation-painting-nizwa/ | شركة عزل أسطح في نزوى | https://www.rukn-eltatawer.com/om/roof-insulation-nizwa/ |
| cross-service-duplicate | 5 | شركة عزل ودهان أسطح في نزوى | https://www.rukn-eltatawer.com/om/roof-insulation-painting-nizwa/ | شركة عزل أسطح في مسقط | https://www.rukn-eltatawer.com/om/roof-insulation-muscat/ |
| cross-service-duplicate | 5 | شركة إنشاء جلسات حدائق في عبري | https://www.rukn-eltatawer.com/om/garden-seating-ibri/ | شركة مكافحة الطيور في صلالة | https://www.rukn-eltatawer.com/om/bird-control-salalah/ |
| cross-service-duplicate | 5 | شركة صيانة ثلاجات في البريمي | https://www.rukn-eltatawer.com/om/fridge-maintenance-al-buraimi/ | شركة صيانة غسالات في مسقط | https://www.rukn-eltatawer.com/om/washer-maintenance-muscat/ |
| cross-service-duplicate | 5 | شركة صيانة مبردات مياه في مسقط | https://www.rukn-eltatawer.com/om/water-cooler-maintenance-muscat/ | شركة صيانة ميكروويف في مسقط | https://www.rukn-eltatawer.com/om/microwave-maintenance-muscat/ |
| cross-service-duplicate | 6 | شركة صيانة بوتاجازات في صور | https://www.rukn-eltatawer.com/om/stove-maintenance-sur/ | شركة صيانة أفران في صور | https://www.rukn-eltatawer.com/om/oven-maintenance-sur/ |
| cross-service-duplicate | 6 | شركة صيانة بوتاجازات في صور | https://www.rukn-eltatawer.com/om/stove-maintenance-sur/ | شركة صيانة أفران في مسقط | https://www.rukn-eltatawer.com/om/oven-maintenance-muscat/ |
| cross-service-duplicate | 6 | شركة صيانة بوتاجازات في الرستاق | https://www.rukn-eltatawer.com/om/stove-maintenance-rustaq/ | شركة صيانة ثلاجات وتبريد تجاري في البريمي | https://www.rukn-eltatawer.com/om/commercial-refrigeration-maintenance-al-buraimi/ |
| cross-service-duplicate | 6 | شركة تغليف أثاث احترافي في نزوى | https://www.rukn-eltatawer.com/om/furniture-packaging-nizwa/ | شركة عزل خزانات في صور | https://www.rukn-eltatawer.com/om/tank-insulation-sur/ |
| cross-service-duplicate | 6 | شركة عزل خزانات في عبري | https://www.rukn-eltatawer.com/om/tank-insulation-ibri/ | شركة عزل مطابخ في الرستاق | https://www.rukn-eltatawer.com/om/kitchen-insulation-rustaq/ |
| cross-service-duplicate | 6 | شركة عزل خزانات في نزوى | https://www.rukn-eltatawer.com/om/tank-insulation-nizwa/ | شركة عزل مطابخ في الرستاق | https://www.rukn-eltatawer.com/om/kitchen-insulation-rustaq/ |
| cross-service-duplicate | 6 | شركة تنظيف منازل في صور | https://www.rukn-eltatawer.com/om/home-cleaning-sur/ | شركة تنظيف مستشفيات وعيادات في صحار | https://www.rukn-eltatawer.com/om/hospital-clinic-cleaning-sohar/ |
| cross-service-duplicate | 6 | شركة صيانة سباكة في صلالة | https://www.rukn-eltatawer.com/om/plumbing-maintenance-salalah/ | شركة صيانة سخانات في صور | https://www.rukn-eltatawer.com/om/water-heater-maintenance-sur/ |
| cross-service-duplicate | 6 | شركة تركيب إنارة داخلية وخارجية في صحار | https://www.rukn-eltatawer.com/om/indoor-outdoor-lighting-installation-sohar/ | شركة سباك منازل في صحار | https://www.rukn-eltatawer.com/om/home-plumber-elec-sohar/ |
| cross-service-duplicate | 6 | شركة كهربائي منازل في صلالة | https://www.rukn-eltatawer.com/om/home-electrician-elec-salalah/ | كهربائي منازل في صحار | https://www.rukn-eltatawer.com/om/home-electrician-sohar/ |
| cross-service-duplicate | 6 | شركة عزل ودهان أسطح في عبري | https://www.rukn-eltatawer.com/om/roof-insulation-painting-ibri/ | شركة عزل أسطح في مسقط | https://www.rukn-eltatawer.com/om/roof-insulation-muscat/ |
| cross-service-duplicate | 6 | شركة عزل ودهان أسطح في صلالة | https://www.rukn-eltatawer.com/om/roof-insulation-painting-salalah/ | شركة عزل أسطح في عبري | https://www.rukn-eltatawer.com/om/roof-insulation-ibri/ |
| cross-service-duplicate | 6 | شركة عزل ودهان أسطح في صحار | https://www.rukn-eltatawer.com/om/roof-insulation-painting-sohar/ | شركة عزل مائي في صحار | https://www.rukn-eltatawer.com/om/waterproofing-sohar/ |
| cross-service-duplicate | 6 | شركة عزل مائي في البريمي | https://www.rukn-eltatawer.com/om/waterproofing-al-buraimi/ | شركة عزل أسطح في مسقط | https://www.rukn-eltatawer.com/om/roof-insulation-muscat/ |
| cross-service-duplicate | 6 | شركة تركيب وصيانة سخانات مركزية في عبري | https://www.rukn-eltatawer.com/om/central-heater-installation-maintenance-ibri/ | شركة تركيب عشب صناعي في عبري | https://www.rukn-eltatawer.com/om/artificial-grass-ibri/ |
| cross-service-duplicate | 6 | شركة تنظيف وتزيين الحدائق في عبري | https://www.rukn-eltatawer.com/om/garden-cleaning-ibri/ | شركة تنظيف مراتب في صلالة | https://www.rukn-eltatawer.com/om/mattress-cleaning-salalah/ |
| cross-service-duplicate | 6 | شركة عزل صوتي في صلالة | https://www.rukn-eltatawer.com/om/soundproofing-salalah/ | شركة عزل مطابخ في صلالة | https://www.rukn-eltatawer.com/om/kitchen-insulation-salalah/ |
| cross-service-duplicate | 7 | شركة التعقيم بالأوزون في البريمي | https://www.rukn-eltatawer.com/om/ozone-disinfection-al-buraimi/ | شركة تنظيف كنب في مسقط | https://www.rukn-eltatawer.com/om/sofa-cleaning-muscat/ |
| cross-service-duplicate | 7 | شركة صيانة نشافات في صور | https://www.rukn-eltatawer.com/om/dryer-maintenance-sur/ | شركة صيانة مباني في الرستاق | https://www.rukn-eltatawer.com/om/building-maintenance-rustaq/ |
| cross-service-duplicate | 7 | شركة صيانة مباني في الرستاق | https://www.rukn-eltatawer.com/om/building-maintenance-rustaq/ | شركة صيانة مبردات مياه في صلالة | https://www.rukn-eltatawer.com/om/water-cooler-maintenance-salalah/ |
| cross-service-duplicate | 7 | شركة تنظيف موكيت في البريمي | https://www.rukn-eltatawer.com/om/moquette-cleaning-al-buraimi/ | شركة تنظيف مستشفيات وعيادات في البريمي | https://www.rukn-eltatawer.com/om/hospital-clinic-cleaning-al-buraimi/ |
| cross-service-duplicate | 7 | شركة صيانة ميكروويف في البريمي | https://www.rukn-eltatawer.com/om/microwave-maintenance-al-buraimi/ | شركة صيانة غسالات في عبري | https://www.rukn-eltatawer.com/om/washer-maintenance-ibri/ |
| cross-service-duplicate | 7 | شركة صيانة مبردات مياه في الرستاق | https://www.rukn-eltatawer.com/om/water-cooler-maintenance-rustaq/ | شركة صيانة غسالات في عبري | https://www.rukn-eltatawer.com/om/washer-maintenance-ibri/ |
| cross-service-duplicate | 7 | شركة تصميم حدائق داخلية في البريمي | https://www.rukn-eltatawer.com/om/indoor-garden-design-al-buraimi/ | شركة تنظيف خزانات مياه في نزوى | https://www.rukn-eltatawer.com/om/water-tank-cleaning-nizwa/ |

_91 صفاً إضافياً في ملف CSV._

### نفس الخدمة في مدن مختلفة (نسخ مدينة)

| النوع | المسافة | عنوان أ | رابط أ | عنوان ب | رابط ب |
| --- | --- | --- | --- | --- | --- |
| city-variant-template | 2 | شركة صيانة ثلاجات في نزوى | https://www.rukn-eltatawer.com/om/fridge-maintenance-nizwa/ | شركة صيانة ثلاجات في صلالة | https://www.rukn-eltatawer.com/om/fridge-maintenance-salalah/ |
| city-variant-template | 2 | شركة تخزين أثاث في صور | https://www.rukn-eltatawer.com/om/furniture-storage-sur/ | شركة تخزين أثاث في صلالة | https://www.rukn-eltatawer.com/om/furniture-storage-salalah/ |
| city-variant-template | 2 | شركة عزل خزانات في عبري | https://www.rukn-eltatawer.com/om/tank-insulation-ibri/ | شركة عزل خزانات في نزوى | https://www.rukn-eltatawer.com/om/tank-insulation-nizwa/ |
| city-variant-template | 3 | شركة بناء مطابخ خارجية في الرستاق | https://www.rukn-eltatawer.com/om/outdoor-kitchens-rustaq/ | شركة بناء مطابخ خارجية في عبري | https://www.rukn-eltatawer.com/om/outdoor-kitchens-ibri/ |
| city-variant-template | 3 | شركة عزل ودهان أسطح في عبري | https://www.rukn-eltatawer.com/om/roof-insulation-painting-ibri/ | شركة عزل ودهان أسطح في صلالة | https://www.rukn-eltatawer.com/om/roof-insulation-painting-salalah/ |
| city-variant-template | 3 | شركة عزل ودهان أسطح في نزوى | https://www.rukn-eltatawer.com/om/roof-insulation-painting-nizwa/ | شركة عزل ودهان أسطح في مسقط | https://www.rukn-eltatawer.com/om/roof-insulation-painting-muscat/ |
| city-variant-template | 3 | شركة عزل أسطح في عبري | https://www.rukn-eltatawer.com/om/roof-insulation-ibri/ | شركة عزل أسطح في نزوى | https://www.rukn-eltatawer.com/om/roof-insulation-nizwa/ |
| city-variant-template | 3 | شركة تركيب وصيانة فلاتر مياه في البريمي | https://www.rukn-eltatawer.com/om/water-filters-al-buraimi/ | شركة تركيب وصيانة فلاتر مياه في صور | https://www.rukn-eltatawer.com/om/water-filters-sur/ |
| city-variant-template | 4 | شركة بناء مجالس خارجية في نزوى | https://www.rukn-eltatawer.com/om/outdoor-majlis-nizwa/ | شركة بناء مجالس خارجية في مسقط | https://www.rukn-eltatawer.com/om/outdoor-majlis-muscat/ |
| city-variant-template | 4 | فني تركيب دش في البريمي | https://www.rukn-eltatawer.com/om/sat-dish-tech-al-buraimi/ | فني تركيب دش في نزوى | https://www.rukn-eltatawer.com/om/sat-dish-tech-nizwa/ |
| city-variant-template | 4 | شركة صيانة ثلاجات في نزوى | https://www.rukn-eltatawer.com/om/fridge-maintenance-nizwa/ | شركة صيانة ثلاجات في مسقط | https://www.rukn-eltatawer.com/om/fridge-maintenance-muscat/ |
| city-variant-template | 4 | شركة صيانة ثلاجات في صلالة | https://www.rukn-eltatawer.com/om/fridge-maintenance-salalah/ | شركة صيانة ثلاجات في مسقط | https://www.rukn-eltatawer.com/om/fridge-maintenance-muscat/ |
| city-variant-template | 4 | شركة عزل مطابخ في عبري | https://www.rukn-eltatawer.com/om/kitchen-insulation-ibri/ | شركة عزل مطابخ في الرستاق | https://www.rukn-eltatawer.com/om/kitchen-insulation-rustaq/ |
| city-variant-template | 4 | شركة تبطين وصيانة خزانات مياه في نزوى | https://www.rukn-eltatawer.com/om/tank-lining-maintenance-nizwa/ | شركة تبطين وصيانة خزانات مياه في مسقط | https://www.rukn-eltatawer.com/om/tank-lining-maintenance-muscat/ |
| city-variant-template | 4 | شركة عزل ودهان أسطح في عبري | https://www.rukn-eltatawer.com/om/roof-insulation-painting-ibri/ | شركة عزل ودهان أسطح في مسقط | https://www.rukn-eltatawer.com/om/roof-insulation-painting-muscat/ |
| city-variant-template | 4 | شركة عزل أسطح في نزوى | https://www.rukn-eltatawer.com/om/roof-insulation-nizwa/ | شركة عزل أسطح في مسقط | https://www.rukn-eltatawer.com/om/roof-insulation-muscat/ |
| city-variant-template | 4 | شركة صيانة مواسير صرف صحي في عبري | https://www.rukn-eltatawer.com/om/drainage-pipe-maintenance-ibri/ | شركة صيانة مواسير صرف صحي في صحار | https://www.rukn-eltatawer.com/om/drainage-pipe-maintenance-sohar/ |
| city-variant-template | 4 | شركة عزل مطابخ في البريمي | https://www.rukn-eltatawer.com/om/kitchen-insulation-al-buraimi/ | شركة عزل مطابخ في نزوى | https://www.rukn-eltatawer.com/om/kitchen-insulation-nizwa/ |
| city-variant-template | 5 | شركة تخزين أثاث في البريمي | https://www.rukn-eltatawer.com/om/furniture-storage-al-buraimi/ | شركة تخزين أثاث في صور | https://www.rukn-eltatawer.com/om/furniture-storage-sur/ |
| city-variant-template | 5 | شركة تخزين أثاث في البريمي | https://www.rukn-eltatawer.com/om/furniture-storage-al-buraimi/ | شركة تخزين أثاث في صلالة | https://www.rukn-eltatawer.com/om/furniture-storage-salalah/ |

_103 صفاً إضافياً في ملف CSV._

## 4) مقالات لا يتناسب محتواها مع العنوان أو الموضوع أو الخدمة

| العنوان | الرابط | كلمات | كلمات فريدة | المدينة | الملاحظة |
| --- | --- | --- | --- | --- | --- |
| شركة شحن دولي جوي في الرستاق | https://www.rukn-eltatawer.com/om/air-freight-rustaq/ | 2658 | 1688 | rustaq | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 36%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة شحن دولي جوي في عبري | https://www.rukn-eltatawer.com/om/air-freight-ibri/ | 2612 | 1547 | ibri | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 41%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة شحن دولي جوي في البريمي | https://www.rukn-eltatawer.com/om/air-freight-al-buraimi/ | 2584 | 1656 | al-buraimi | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 36%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة شحن دولي جوي في صور | https://www.rukn-eltatawer.com/om/air-freight-sur/ | 2606 | 1676 | sur | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 36%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة شحن دولي جوي في صحار | https://www.rukn-eltatawer.com/om/air-freight-sohar/ | 2572 | 1634 | sohar | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 36%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة شحن دولي جوي في نزوى | https://www.rukn-eltatawer.com/om/air-freight-nizwa/ | 2612 | 1539 | nizwa | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 41%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة شحن دولي جوي في صلالة | https://www.rukn-eltatawer.com/om/air-freight-salalah/ | 2647 | 1742 | salalah | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 34%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة شحن دولي جوي في مسقط | https://www.rukn-eltatawer.com/om/air-freight-muscat/ | 2731 | 1620 | muscat | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 41%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة شحن سيارات في الرستاق | https://www.rukn-eltatawer.com/om/car-shipping-rustaq/ | 2579 | 1622 | rustaq | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 37%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة شحن سيارات في عبري | https://www.rukn-eltatawer.com/om/car-shipping-ibri/ | 2511 | 1658 | ibri | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 34%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة شحن سيارات في البريمي | https://www.rukn-eltatawer.com/om/car-shipping-al-buraimi/ | 2549 | 1697 | al-buraimi | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 33%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة شحن سيارات في صور | https://www.rukn-eltatawer.com/om/car-shipping-sur/ | 2558 | 1516 | sur | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 41%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة شحن سيارات في نزوى | https://www.rukn-eltatawer.com/om/car-shipping-nizwa/ | 2607 | 1535 | nizwa | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 41%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة شحن سيارات في صحار | https://www.rukn-eltatawer.com/om/car-shipping-sohar/ | 2552 | 1624 | sohar | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 36%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة شحن سيارات في صلالة | https://www.rukn-eltatawer.com/om/car-shipping-salalah/ | 2568 | 1638 | salalah | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 36%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة شحن سيارات في مسقط | https://www.rukn-eltatawer.com/om/car-shipping-muscat/ | 2673 | 1689 | muscat | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 37%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة شحن بضائع في الرستاق | https://www.rukn-eltatawer.com/om/cargo-shipping-rustaq/ | 2565 | 1652 | rustaq | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 36%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة شحن بضائع في عبري | https://www.rukn-eltatawer.com/om/cargo-shipping-ibri/ | 2550 | 1634 | ibri | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 36%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة شحن بضائع في البريمي | https://www.rukn-eltatawer.com/om/cargo-shipping-al-buraimi/ | 2549 | 1650 | al-buraimi | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 35%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة شحن بضائع في صور | https://www.rukn-eltatawer.com/om/cargo-shipping-sur/ | 2573 | 1673 | sur | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 35%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة شحن بضائع في نزوى | https://www.rukn-eltatawer.com/om/cargo-shipping-nizwa/ | 2557 | 1676 | nizwa | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 34%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة شحن بضائع في صحار | https://www.rukn-eltatawer.com/om/cargo-shipping-sohar/ | 2557 | 1666 | sohar | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 35%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة شحن بضائع في صلالة | https://www.rukn-eltatawer.com/om/cargo-shipping-salalah/ | 2596 | 1605 | salalah | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 38%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة شحن بضائع في مسقط | https://www.rukn-eltatawer.com/om/cargo-shipping-muscat/ | 2671 | 1776 | muscat | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 34%. تشابه مرتفع (hamming=8, cross-service-duplicate) مع https://www.rukn-eltatawer.com/om/... |
| شركة صيانة كاميرات مراقبة في البريمي | https://www.rukn-eltatawer.com/om/cctv-maintenance-al-buraimi/ | 2483 | 1552 | al-buraimi | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 38%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة صيانة كاميرات مراقبة في عبري | https://www.rukn-eltatawer.com/om/cctv-maintenance-ibri/ | 2452 | 1464 | ibri | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 40%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة صيانة كاميرات مراقبة في الرستاق | https://www.rukn-eltatawer.com/om/cctv-maintenance-rustaq/ | 2470 | 1519 | rustaq | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 38%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة صيانة كاميرات مراقبة في صور | https://www.rukn-eltatawer.com/om/cctv-maintenance-sur/ | 2481 | 1510 | sur | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 39%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة صيانة كاميرات مراقبة في نزوى | https://www.rukn-eltatawer.com/om/cctv-maintenance-nizwa/ | 2491 | 1520 | nizwa | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 39%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة صيانة كاميرات مراقبة في صحار | https://www.rukn-eltatawer.com/om/cctv-maintenance-sohar/ | 2484 | 1423 | sohar | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 43%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة صيانة كاميرات مراقبة في صلالة | https://www.rukn-eltatawer.com/om/cctv-maintenance-salalah/ | 2568 | 1536 | salalah | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 40%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة صيانة كاميرات مراقبة في مسقط | https://www.rukn-eltatawer.com/om/cctv-maintenance-muscat/ | 2564 | 1549 | muscat | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 40%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| فني تركيب كاميرات مراقبة في البريمي | https://www.rukn-eltatawer.com/om/cctv-tech-al-buraimi/ | 2433 | 1599 | al-buraimi | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 34%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| فني تركيب كاميرات مراقبة في عبري | https://www.rukn-eltatawer.com/om/cctv-tech-ibri/ | 2427 | 1567 | ibri | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 35%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| فني تركيب كاميرات مراقبة في الرستاق | https://www.rukn-eltatawer.com/om/cctv-tech-rustaq/ | 2482 | 1627 | rustaq | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 34%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| فني تركيب كاميرات مراقبة في صور | https://www.rukn-eltatawer.com/om/cctv-tech-sur/ | 2528 | 1556 | sur | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 38%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| فني تركيب كاميرات مراقبة في نزوى | https://www.rukn-eltatawer.com/om/cctv-tech-nizwa/ | 2494 | 1551 | nizwa | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 38%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| فني تركيب كاميرات مراقبة في صحار | https://www.rukn-eltatawer.com/om/cctv-tech-sohar/ | 2469 | 1549 | sohar | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 37%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| فني تركيب كاميرات مراقبة في صلالة | https://www.rukn-eltatawer.com/om/cctv-tech-salalah/ | 2514 | 1603 | salalah | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 36%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| فني تركيب كاميرات مراقبة في مسقط | https://www.rukn-eltatawer.com/om/cctv-tech-muscat/ | 2571 | 1715 | muscat | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 33%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة تركيب وصيانة سخانات مركزية في صحار | https://www.rukn-eltatawer.com/om/central-heater-installation-maintenance-sohar/ | 2628 | 1632 | sohar | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 38%. تشابه مرتفع (hamming=8, city-variant-template) مع https://www.rukn-eltatawer.com/om/ce... |
| شركة تركيب وصيانة سخانات مركزية في صلالة | https://www.rukn-eltatawer.com/om/central-heater-installation-maintenance-salalah/ | 2672 | 1773 | salalah | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 34%. المحتوى يميل لخدمة «cleaning» (13) أكثر من خدمة المقال «plumbing» (2). نموذج المقال يس... |
| شركة شحن داخلي داخل في عبري | https://www.rukn-eltatawer.com/om/domestic-shipping-ibri/ | 2601 | 1616 | ibri | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 38%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة شحن داخلي داخل في الرستاق | https://www.rukn-eltatawer.com/om/domestic-shipping-rustaq/ | 2671 | 1680 | rustaq | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 37%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة شحن داخلي داخل في البريمي | https://www.rukn-eltatawer.com/om/domestic-shipping-al-buraimi/ | 2593 | 1663 | al-buraimi | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 36%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة شحن داخلي داخل في صور | https://www.rukn-eltatawer.com/om/domestic-shipping-sur/ | 2670 | 1687 | sur | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 37%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة شحن داخلي داخل في نزوى | https://www.rukn-eltatawer.com/om/domestic-shipping-nizwa/ | 2692 | 1702 | nizwa | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 37%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة شحن داخلي داخل في صحار | https://www.rukn-eltatawer.com/om/domestic-shipping-sohar/ | 2653 | 1712 | sohar | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 36%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة شحن داخلي داخل في صلالة | https://www.rukn-eltatawer.com/om/domestic-shipping-salalah/ | 2684 | 1716 | salalah | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 36%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة شحن داخلي داخل في مسقط | https://www.rukn-eltatawer.com/om/domestic-shipping-muscat/ | 2721 | 1771 | muscat | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 35%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |

_136 صفاً إضافياً في ملف CSV._

خدمات خارج نطاق الصفحة الرئيسية (شحن، نقل، ستالايت، كاميرات، مصاعد، طاقة شمسية):

`shipping-offices` ×8, `sea-freight` ×8, `satellite-tech` ×8, `sat-dish-tech` ×8, `piano-moving` ×8, `outdoor-moving` ×8, `land-freight` ×8, `indoor-moving` ×8, `home-audio-tech` ×8, `furniture-storage` ×8, `furniture-shipping` ×8, `cargo-shipping` ×8, `car-shipping` ×8, `air-freight` ×8, `furniture-packaging` ×8, `furniture-moving-packaging` ×8, `express-parcel-shipping` ×8, `elevator-maintenance` ×8, `domestic-shipping` ×8, `cctv-maintenance` ×8, `cctv-tech` ×8, `solar-systems-installation` ×8, `solar-water-heaters` ×8

## 5) الأخطاء والنواقص

| نوع النقص | مقالات |
| --- | --- |
| شورت كود ظاهر | 0 |
| عبارة ناقصة | 1244 |
| بقايا إمارات | 0 |
| نموذج هاتف إماراتي 05 | 1648 |
| تصنيف مدينة/خدمة مفقود | 0 |
| بدون صورة بارزة | 0 |
| صورة بارزة مكررة | 1496 |
| خطأ هيكلي | 51 |
| نص نائب | 0 |
| بدون H2 | 0 |

أكثر الصور البارزة تكراراً:

| رقم الصورة | عدد المقالات |
| --- | --- |
| 245 | 1353 |
| 426 | 87 |
| 246 | 56 |
| 390 | 8 |
| 300 | 8 |

| العنوان | الرابط | كلمات | كلمات فريدة | المدينة | الملاحظة |
| --- | --- | --- | --- | --- | --- |
| شركة تركيب طابوق في عبري | https://www.rukn-eltatawer.com/om/brickwork-ibri/ | 2360 | 1464 | ibri | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 38%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة تركيب طابوق في صحار | https://www.rukn-eltatawer.com/om/brickwork-sohar/ | 2383 | 1446 | sohar | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 39%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة تركيب طابوق في الرستاق | https://www.rukn-eltatawer.com/om/brickwork-rustaq/ | 2389 | 1536 | rustaq | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 36%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة بناء ملاحق في عبري | https://www.rukn-eltatawer.com/om/annex-building-ibri/ | 2397 | 1447 | ibri | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 40%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة بناء ملاحق في صور | https://www.rukn-eltatawer.com/om/annex-building-sur/ | 2405 | 1525 | sur | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 37%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة بناء ملاحق في البريمي | https://www.rukn-eltatawer.com/om/annex-building-al-buraimi/ | 2407 | 1410 | al-buraimi | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 41%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة تركيب طابوق في البريمي | https://www.rukn-eltatawer.com/om/brickwork-al-buraimi/ | 2409 | 1481 | al-buraimi | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 38%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة بناء أسوار طابوق في البريمي | https://www.rukn-eltatawer.com/om/block-fences-al-buraimi/ | 2410 | 1422 | al-buraimi | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 41%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة بناء أسوار طابوق في الرستاق | https://www.rukn-eltatawer.com/om/block-fences-rustaq/ | 2414 | 1481 | rustaq | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 39%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة تركيب طابوق في صلالة | https://www.rukn-eltatawer.com/om/brickwork-salalah/ | 2421 | 1646 | salalah | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 32%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة صيانة أبواب أوتوماتيكية في عبري | https://www.rukn-eltatawer.com/om/automatic-doors-maintenance-ibri/ | 2423 | 1458 | ibri | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 40%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة تركيب طابوق في نزوى | https://www.rukn-eltatawer.com/om/brickwork-nizwa/ | 2426 | 1572 | nizwa | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 35%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| فني تركيب كاميرات مراقبة في عبري | https://www.rukn-eltatawer.com/om/cctv-tech-ibri/ | 2427 | 1567 | ibri | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 35%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة تركيب طابوق في صور | https://www.rukn-eltatawer.com/om/brickwork-sur/ | 2430 | 1424 | sur | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 41%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| فني تركيب كاميرات مراقبة في البريمي | https://www.rukn-eltatawer.com/om/cctv-tech-al-buraimi/ | 2433 | 1599 | al-buraimi | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 34%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة بناء أسوار طابوق في صور | https://www.rukn-eltatawer.com/om/block-fences-sur/ | 2434 | 1565 | sur | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 36%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة بناء أسوار طابوق في عبري | https://www.rukn-eltatawer.com/om/block-fences-ibri/ | 2438 | 1486 | ibri | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 39%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة بناء أسوار طابوق في نزوى | https://www.rukn-eltatawer.com/om/block-fences-nizwa/ | 2438 | 1412 | nizwa | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 42%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة صيانة أبواب أوتوماتيكية في الرستاق | https://www.rukn-eltatawer.com/om/automatic-doors-maintenance-rustaq/ | 2440 | 1582 | rustaq | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 35%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة صيانة مصاعد في عبري | https://www.rukn-eltatawer.com/om/elevator-maintenance-ibri/ | 2443 | 1507 | ibri | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 38%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة صيانة مصاعد في البريمي | https://www.rukn-eltatawer.com/om/elevator-maintenance-al-buraimi/ | 2445 | 1556 | al-buraimi | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 36%. تشابه مرتفع (hamming=8, cross-service-duplicate) مع https://www.rukn-eltatawer.com/om/... |
| شركة بناء ملاحق في الرستاق | https://www.rukn-eltatawer.com/om/annex-building-rustaq/ | 2446 | 1571 | rustaq | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 36%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة صيانة أبواب أوتوماتيكية في البريمي | https://www.rukn-eltatawer.com/om/automatic-doors-maintenance-al-buraimi/ | 2452 | 1359 | al-buraimi | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 45%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة صيانة كاميرات مراقبة في عبري | https://www.rukn-eltatawer.com/om/cctv-maintenance-ibri/ | 2452 | 1464 | ibri | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 40%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة بناء أسوار طابوق في صحار | https://www.rukn-eltatawer.com/om/block-fences-sohar/ | 2455 | 1623 | sohar | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 34%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة صيانة مصاعد في نزوى | https://www.rukn-eltatawer.com/om/elevator-maintenance-nizwa/ | 2456 | 1526 | nizwa | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 38%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة بناء ملاحق في صحار | https://www.rukn-eltatawer.com/om/annex-building-sohar/ | 2456 | 1435 | sohar | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 42%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة صيانة مصاعد في صحار | https://www.rukn-eltatawer.com/om/elevator-maintenance-sohar/ | 2460 | 1493 | sohar | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 39%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة بناء ملاحق في نزوى | https://www.rukn-eltatawer.com/om/annex-building-nizwa/ | 2460 | 1543 | nizwa | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 37%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| فني تركيب كاميرات مراقبة في صحار | https://www.rukn-eltatawer.com/om/cctv-tech-sohar/ | 2469 | 1549 | sohar | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 37%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة بناء ملاحق في صلالة | https://www.rukn-eltatawer.com/om/annex-building-salalah/ | 2470 | 1602 | salalah | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 35%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة صيانة كاميرات مراقبة في الرستاق | https://www.rukn-eltatawer.com/om/cctv-maintenance-rustaq/ | 2470 | 1519 | rustaq | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 38%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة تركيب طابوق في مسقط | https://www.rukn-eltatawer.com/om/brickwork-muscat/ | 2473 | 1457 | muscat | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 41%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة صيانة مصاعد في صور | https://www.rukn-eltatawer.com/om/elevator-maintenance-sur/ | 2477 | 1426 | sur | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 42%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة صيانة أبواب أوتوماتيكية في صحار | https://www.rukn-eltatawer.com/om/automatic-doors-maintenance-sohar/ | 2480 | 1523 | sohar | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 39%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة صيانة أبواب أوتوماتيكية في نزوى | https://www.rukn-eltatawer.com/om/automatic-doors-maintenance-nizwa/ | 2481 | 1625 | nizwa | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 34%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |
| شركة تركيب وصيانة فلاتر مياه في عبري | https://www.rukn-eltatawer.com/om/water-filters-ibri/ | 2481 | 1567 | ibri | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 37%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. صورة بارزة مكررة على... |
| شركة صيانة كاميرات مراقبة في صور | https://www.rukn-eltatawer.com/om/cctv-maintenance-sur/ | 2481 | 1510 | sur | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 39%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| فني تركيب كاميرات مراقبة في الرستاق | https://www.rukn-eltatawer.com/om/cctv-tech-rustaq/ | 2482 | 1627 | rustaq | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 34%. الخدمة خارج نطاق الموقع المعلن في الصفحة الرئيسية (شحن/نقل/ستالايت/كاميرات/مصاعد/طاقة ... |
| شركة صيانة أبواب أوتوماتيكية في صلالة | https://www.rukn-eltatawer.com/om/automatic-doors-maintenance-salalah/ | 2483 | 1478 | salalah | هيكل H2 مكرر على 1648 مقالة، ونسبة جمل القالب 40%. نموذج المقال يستخدم خانة هاتف إماراتية 05xxxxxxxx بدل رقم عُماني. عبارة ناقصة «تغطية ح... |

_1608 صفاً إضافياً في ملف CSV._

## التوصيات

1. لا تكتب مقالات جديدة الآن. الكمية كافية؛ المشكلة في التكرار لا في النقص العددي.
2. أعد كتابة المقدمة وFAQ والدليل المحلي لكل خدمة×مدينة حتى لا تبقى الثماني المدن نسخة واحدة.
3. ادمج أو فرّق المقالات المتشابهة عبر خدمتين مختلفتين (Hamming منخفض).
4. احذف أو حوّل خدمات الشحن/النقل/الستالايت/المصاعد إن لم تقدموها فعلياً في عُمان.
5. أكمل عبارة «تغطية حسب الاتفاق:» بصورة بارزة خاصة بكل خدمة، لا صورة واحدة لكل الموقع.
6. صفحتا `/services/{slug}/` والمحاور (من نحن، المدن، اتصل بنا) قصيرة ويجب إغناؤها أو عدم فهرستها كمنافس للمقالات.

التفاصيل الكاملة: `docs/oman-posts-quality-audit.csv` و`docs/oman-posts-quality-audit-pairs.csv`.
