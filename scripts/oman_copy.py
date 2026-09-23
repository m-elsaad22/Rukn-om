"""Unique Arabic + English copy for Oman cleaning service × city pages."""

from __future__ import annotations

CITIES = {
    "muscat": {
        "ar": "مسقط",
        "en": "Muscat",
        "prep": "بمسقط",
        "gov_ar": "محافظة مسقط",
        "gov_en": "Muscat Governorate",
        "areas_ar": "روي، مطرح، القرم، الشاطئ، الخوير، بوشر، غلا، العذيبة، الموج، السيب، العامرات، قريات",
        "areas_en": "Ruwi, Muttrah, Qurum, Shatti Al Qurum, Al Khuwair, Bausher, Ghala, Azaiba, Al Mouj, Seeb, Amerat and Quriyat",
        "climate_ar": "رطوبة ساحلية صيفاً وغبار موسمي يدخل الشقق عبر النوافذ والمكيفات، مع رخام وأرضيات لامعة في الفلل الساحلية",
        "climate_en": "coastal humidity in summer and seasonal dust that settles in apartments through windows and AC vents, plus marble floors in seaside villas",
        "stock_ar": "شقق في الخوير وبوشر، فلل في القرم والموج، ومبانٍ أقدم في مطرح وروي تحتاج عناية بالرطوبة",
        "stock_en": "apartments in Al Khuwair and Bausher, villas in Qurum and Al Mouj, and older buildings in Muttrah and Ruwi that hold humidity",
        "note_ar": "مسقط عاصمة إدارية وتجارية؛ مواعيد العمل في الوزارات والمجمعات تختلف عن البيوت في السيب والعامرات",
        "note_en": "Muscat is the administrative capital; ministry and mall schedules differ from family homes in Seeb and Amerat",
    },
    "salalah": {
        "ar": "صلالة",
        "en": "Salalah",
        "prep": "بصلالة",
        "gov_ar": "محافظة ظفار",
        "gov_en": "Dhofar Governorate",
        "areas_ar": "الحافة، عوقد، الدهاريز، صلالة الوسطى، طاقة، مرباط، المغسيل",
        "areas_en": "Al Haffa, Awqad, Dahariz, central Salalah, Taqah, Mirbat and Mughsail",
        "climate_ar": "موسم الخريف يزيد الرطوبة والعفن على الجدران والستائر والمفروشات، بخلاف باقي مدن السلطنة الجافة",
        "climate_en": "the Khareef monsoon raises humidity and mould on walls, curtains and upholstery unlike the dry interior of Oman",
        "stock_ar": "فلل سياحية وشقق للعائلات، مع مجالس واسعة ونوافذ كبيرة تواجه الرذاذ الملحي",
        "stock_en": "holiday villas and family apartments, with large majlis rooms and windows exposed to salt spray",
        "note_ar": "ذروة الطلب بين يونيو وسبتمبر مع السياحة؛ الحجوزات المبكرة ضرورية في الخريف",
        "note_en": "demand peaks from June to September with tourism; advance booking is essential during Khareef",
    },
    "nizwa": {
        "ar": "نزوى",
        "en": "Nizwa",
        "prep": "بنزوى",
        "gov_ar": "محافظة الداخلية",
        "gov_en": "Ad Dakhiliyah Governorate",
        "areas_ar": "نزوى، بهلاء، إزكي، منح، سمائل، بركة الموز",
        "areas_en": "Nizwa, Bahla, Izki, Manah, Samail and Birkat Al Mouz",
        "climate_ar": "حرارة داخلية جافة وغبار ترابي من الأودية، مع رطوبة موضعية حول الأفلاج والمزروعات",
        "climate_en": "dry inland heat and wadi dust, with local humidity around aflaj irrigation and planted plots",
        "stock_ar": "بيوت تقليدية قرب السوق والحصن، وفلل حديثة على أطراف المدينة بواجهات حجرية",
        "stock_en": "traditional houses near the souq and fort, and newer villas on the city edge with stone facades",
        "note_ar": "الجمعة يوم السوق الأسبوعي؛ نرتّب الزيارات حول حركة الحصن والسوق",
        "note_en": "Friday is the weekly souq day; visits are scheduled around fort and market traffic",
    },
    "sohar": {
        "ar": "صحار",
        "en": "Sohar",
        "prep": "بصحار",
        "gov_ar": "شمال الباطنة",
        "gov_en": "North Al Batinah",
        "areas_ar": "صحار، مجيس، لوى، شناص، صحار الصناعية، حي النزهة",
        "areas_en": "Sohar, Majis, Liwa, Shinas, Sohar Industrial and Al Nuzha",
        "climate_ar": "رطوبة ساحل الباطنة مع غبار صناعي قرب الميناء ومجمع الألمنيوم والصلب",
        "climate_en": "Batinah coastal humidity plus industrial dust near the port, aluminium and steel complex",
        "stock_ar": "فلل سكنية للموظفين، شقق عمالية، ومكاتب قرب المنطقة الحرة",
        "stock_en": "staff villas, workforce apartments and offices near the free zone",
        "note_ar": "نفرّق بين تنظيف البيوت وتنظيف المنشآت الصناعية من حيث المواد وجدول الورديات",
        "note_en": "domestic cleaning is scheduled separately from industrial sites because of chemicals and shift patterns",
    },
    "sur": {
        "ar": "صور",
        "en": "Sur",
        "prep": "بصور",
        "gov_ar": "جنوب الشرقية",
        "gov_en": "South Ash Sharqiyah",
        "areas_ar": "صور، العيجة، رأس الحد، طيوي، جعلان بني بو حسن القريبة",
        "areas_en": "Sur, Al Ayjah, Ras Al Hadd, Tiwi and nearby Jaalan Bani Bu Hassan",
        "climate_ar": "هواء بحري مالح يترك طبقة على الزجاج والألمنيوم والرخام الخارجي",
        "climate_en": "salty sea air leaves a film on glass, aluminium and outdoor marble",
        "stock_ar": "بيوت صيادين تقليدية، فلل ساحلية، واستراحات على طريق رأس الحد",
        "stock_en": "traditional fishing-family houses, coastal villas and rest houses on the Ras Al Hadd road",
        "note_ar": "المسافة من مسقط تعني جدولة يوم كامل للفريق مع مواد كافية في السيارة",
        "note_en": "the distance from Muscat means a full-day crew plan with extra supplies in the van",
    },
    "al-buraimi": {
        "ar": "البريمي",
        "en": "Al Buraimi",
        "prep": "بالبريمي",
        "gov_ar": "محافظة البريمي",
        "gov_en": "Al Buraimi Governorate",
        "areas_ar": "البريمي، محضة، السنينة، حي النهضة",
        "areas_en": "Al Buraimi, Mahdah, As Sunaynah and Al Nahda",
        "climate_ar": "مناخ حدودي جاف ورمال ناعمة تدخل المجالس والسجاد من الأفنية المفتوحة",
        "climate_en": "dry border climate and fine sand that blows into majlis rooms and carpets from open courtyards",
        "stock_ar": "فلل واسعة، مجالس أرضية، ومبانٍ حكومية وتجارية قرب منفذ حفيت",
        "stock_en": "large villas, floor-seating majlis rooms, and government or commercial buildings near the Hafit crossing",
        "note_ar": "التنسيق مع العميل مهم لمواعيد الحدود والتنقل من العين؛ التسعير بالريال العُماني",
        "note_en": "appointment timing considers the border with Al Ain; quotes are issued in Omani rial, not UAE dirham",
    },
    "ibri": {
        "ar": "عبري",
        "en": "Ibri",
        "prep": "بعبري",
        "gov_ar": "محافظة الظاهرة",
        "gov_en": "Ad Dhahirah Governorate",
        "areas_ar": "عبري، ينقل، ضنك، حي السليف",
        "areas_en": "Ibri, Yanqul, Dhank and Al Sulayf",
        "climate_ar": "حرارة صحراوية وغبار أحمر يلتصق بالستائر والمكيفات والخزانات",
        "climate_en": "desert heat and red dust that clings to curtains, AC units and water tanks",
        "stock_ar": "بيوت طينية مجددة وفلل إسمنتية مع أحواش ترابية تحتاج كنساً رطباً لا جافاً",
        "stock_en": "restored earthen houses and concrete villas with dusty yards that need damp mopping, not dry sweeping",
        "note_ar": "المدينة خدمة لمحور الظاهرة؛ نغطي ينقل وضنك في الرحلة نفسها عند الاتفاق",
        "note_en": "Ibri is the hub for Dhahirah; Yanqul and Dhank can be combined in one trip when booked together",
    },
    "rustaq": {
        "ar": "الرستاق",
        "en": "Rustaq",
        "prep": "بالرستاق",
        "gov_ar": "جنوب الباطنة",
        "gov_en": "South Al Batinah",
        "areas_ar": "الرستاق، نخل، وادي بني خروص، العوابي، الحوقين",
        "areas_en": "Rustaq, Nakhal, Wadi Bani Kharus, Al Awabi and Hawqayn",
        "climate_ar": "مزيج جبلي وساحلي: رطوبة الأودية وعيون الماء مع غبار الطرق الجبلية",
        "climate_en": "a mountain-coast mix: wadi and spring humidity plus dust from mountain roads",
        "stock_ar": "بيوت قرب الحصن والعين، واستراحات وادي، وفلل حديثة في المخططات الجديدة",
        "stock_en": "houses near the fort and hot spring, wadi rest houses, and newer villas in planned neighbourhoods",
        "note_ar": "طرق الأودية قد تتأثر بالأمطار؛ نؤكد الموعد صباح يوم التنفيذ",
        "note_en": "wadi roads can be affected by rain; the crew confirms the slot on the morning of the visit",
    },
}

SERVICES = {
    "home-cleaning": {
        "ar": "تنظيف المنازل",
        "en": "house cleaning",
        "title_ar": "شركة تنظيف منازل",
        "title_en": "House Cleaning",
        "kw_ar": "تنظيف منزل",
        "method_ar": "نبدأ بالغرف الأكثر استخداماً ثم المطبخ والحمامات، مع فصل أدوات الأرضيات عن أسطح الطعام",
        "method_en": "We start with high-traffic rooms, then the kitchen and bathrooms, keeping floor tools separate from food-prep surfaces",
        "risk_ar": "الغبار العُماني يخدش الأرضيات إن كُنس جافاً؛ نستخدم كناساً رطباً ومواد لا تترك طبقة لزجة في الرطوبة",
        "risk_en": "Omani dust scratches floors if swept dry; we use damp methods and residues that will not stay sticky in humidity",
        "faq_ar": "هل تنظفون الشقق والفلل في نفس اليوم؟",
        "faq_en": "Do you clean apartments and villas on the same day?",
        "ans_ar": "نعم حسب المساحة وجدول الفريق في المدينة، ويُحدَّد بعد وصف الغرف وعدد السكان",
        "ans_en": "Yes, depending on size and the crew roster in that city, confirmed after room count and occupancy",
    },
    "apartment-cleaning": {
        "ar": "تنظيف الشقق",
        "en": "apartment cleaning",
        "title_ar": "شركة تنظيف شقق",
        "title_en": "Apartment Cleaning",
        "kw_ar": "تنظيف شقة",
        "method_ar": "نراعي مصاعد العمارات ومواقف السيارات الضيقة، ونركّز على المطبخ المفتوح والحمام المشترك",
        "method_en": "We plan around building lifts and tight parking, and focus on open kitchens and shared bathrooms",
        "risk_ar": "الشقق العُمانية غالباً متصلة بمكيف مركزي ينقل الغبار بين الغرف إن لم تُغسل فتحات التهوية",
        "risk_en": "Omani apartments often share central AC that moves dust between rooms unless vents are washed",
        "faq_ar": "هل تدخلون مع حارس العمارة؟",
        "faq_en": "Do you coordinate with the building guard?",
        "ans_ar": "نعم، نطلب تعليمات الدخول مسبقاً في مجمعات مسقط وصحار وصلالة",
        "ans_en": "Yes, we collect access instructions in advance for compounds in Muscat, Sohar and Salalah",
    },
    "villa-cleaning": {
        "ar": "تنظيف الفلل",
        "en": "villa cleaning",
        "title_ar": "شركة تنظيف فلل",
        "title_en": "Villa Cleaning",
        "kw_ar": "تنظيف فيلا",
        "method_ar": "نقسّم الفيلا إلى مجلس خارجي وداخلي ومطبخ ملحق وحديقة محيطة حتى لا تنتقل الأتربة للداخل",
        "method_en": "We split the villa into outdoor majlis, indoor rooms, annex kitchen and surrounding yard so dust is not walked back inside",
        "risk_ar": "الأحواش العُمانية مصدر رمل مستمر؛ نغلق الأبواب أثناء الغسيل الرطب وننظف المداخل آخر خطوة",
        "risk_en": "Omani courtyards constantly feed sand indoors; doors stay shut during wet work and entries are cleaned last",
        "faq_ar": "هل تشملون الملحق الخارجي؟",
        "faq_en": "Is the outdoor annex included?",
        "ans_ar": "نعم عند ذكره في المعاينة، ويُسعَّر ضمن مساحة الفيلا بالريال العُماني",
        "ans_en": "Yes when listed during the survey, and it is priced in Omani rial as part of the villa area",
    },
    "palace-cleaning": {
        "ar": "تنظيف القصور والبيوت الكبيرة",
        "en": "palace and large-residence cleaning",
        "title_ar": "شركة تنظيف قصور",
        "title_en": "Palace Cleaning",
        "kw_ar": "تنظيف قصر",
        "method_ar": "فريق أكبر، جدول غرف متتالٍ، وحماية للثريات والرخام المستورد قبل أي مواد كيميائية",
        "method_en": "A larger crew, a room-by-room timetable, and protection for chandeliers and imported marble before any chemicals",
        "risk_ar": "المساحات الواسعة في عُمان تجمع غباراً غير مرئي على الدرج والدهاليز؛ نفحص بالإضاءة الجانبية",
        "risk_en": "Large Omani residences collect invisible dust on stairs and corridors; we inspect with side lighting",
        "faq_ar": "هل تعملون وفق جدول الخصوصية للعائلة؟",
        "faq_en": "Can you follow a family privacy schedule?",
        "ans_ar": "نعم، نحدد أجنحة مغلقة وأوقات لا يُدخل فيها إلا المشرف المتفق عليه",
        "ans_en": "Yes, we mark closed wings and times when only the agreed supervisor may enter",
    },
    "office-cleaning": {
        "ar": "تنظيف المكاتب",
        "en": "office cleaning",
        "title_ar": "شركة تنظيف مكاتب",
        "title_en": "Office Cleaning",
        "kw_ar": "تنظيف مكتب",
        "method_ar": "بعد ساعات الدوام أو قبل الافتتاح، مع تعقيم لوحات المفاتيح ومقابض الأبواب دون تعطيل الخوادم",
        "method_en": "After hours or before opening, sanitising keyboards and door handles without disturbing servers",
        "risk_ar": "غبار مسقط وصحار يتراكم على الأجهزة؛ نستخدم سحباً وليس هواً مضغوطاً يثير الأتربة",
        "risk_en": "Muscat and Sohar dust settles on equipment; we vacuum instead of using compressed air that lifts grit",
        "faq_ar": "هل تقدّمون عقداً شهرياً؟",
        "faq_en": "Do you offer a monthly contract?",
        "ans_ar": "نعم، زيارات ثابتة حسب عدد المكاتب والحمامات، بفاتورة بالريال العُماني",
        "ans_en": "Yes, fixed visits based on desk and washroom count, invoiced in Omani rial",
    },
    "majlis-cleaning": {
        "ar": "تنظيف المجالس",
        "en": "majlis cleaning",
        "title_ar": "شركة تنظيف مجالس",
        "title_en": "Majlis Cleaning",
        "kw_ar": "تنظيف مجلس",
        "method_ar": "نرفع الوسائد ونغسل الأقمشة حسب النوع، ونهتم برائحة الضيافة بعد البخور والقهوة",
        "method_en": "Cushions are lifted and fabrics washed by type, with attention to hospitality odours after incense and coffee",
        "risk_ar": "المجالس العُمانية أرضية؛ الرمل ينحشر تحت السجاد. لا نستخدم غسيلاً يترك رطوبة تحت الفرش في المناخ الرطب",
        "risk_en": "Omani majlis seating is often on the floor; sand packs under carpets. We avoid washes that leave moisture under padding in humid weather",
        "faq_ar": "هل تزيلون رائحة البخور دون إتلاف القماش؟",
        "faq_en": "Can you reduce incense smell without damaging fabric?",
        "ans_ar": "نستخدم بخاراً ومواد منخفضة الرطوبة بعد اختبار خفي في زاوية المجلس",
        "ans_en": "We use steam and low-moisture products after a hidden corner test",
    },
    "school-nursery-cleaning": {
        "ar": "تنظيف المدارس والحضانات",
        "en": "school and nursery cleaning",
        "title_ar": "شركة تنظيف مدارس وحضانات",
        "title_en": "School and Nursery Cleaning",
        "kw_ar": "تنظيف مدرسة",
        "method_ar": "مواد آمنة للأطفال، جداول بعد الدوام، وتعقيم ألعاب ودورات مياه بكثافة أعلى من البيوت",
        "method_en": "Child-safe products, after-school slots, and denser disinfection of toys and washrooms than in homes",
        "risk_ar": "الرطوبة في صلالة ومسقط تزيد نمو الجراثيم على الأسطح المشتركة؛ نكرر الحمامات يومياً في العقود",
        "risk_en": "Humidity in Salalah and Muscat grows germs on shared surfaces; contracted washrooms are repeated daily",
        "faq_ar": "هل تعملون أثناء الإجازة الصيفية؟",
        "faq_en": "Do you work during the summer break?",
        "ans_ar": "نعم، وهذا أنسب لعمق التنظيف قبل العام الدراسي في السلطنة",
        "ans_en": "Yes, and that is the best window for a deep clean before the Omani school year",
    },
    "hospital-clinic-cleaning": {
        "ar": "تنظيف المستشفيات والعيادات",
        "en": "hospital and clinic cleaning",
        "title_ar": "شركة تنظيف مستشفيات وعيادات",
        "title_en": "Hospital and Clinic Cleaning",
        "kw_ar": "تنظيف عيادة",
        "method_ar": "بروتوكول ألوان للقماش، وتعقيم غرف الكشف دون خلط أدوات الأرضيات مع الأسطح الطبية",
        "method_en": "Colour-coded cloths and disinfection of exam rooms without mixing floor tools with clinical surfaces",
        "risk_ar": "لا نخلط خدمة العيادة مع تنظيف منزلي في نفس العدة؛ الغبار العُماني يُعامل كملوث يجب سحبه لا كنسه",
        "risk_en": "Clinic kits are never mixed with domestic kits; Omani dust is treated as a contaminant to vacuum, not sweep",
        "faq_ar": "هل تلتزمون بمواعيد العيادة؟",
        "faq_en": "Do you follow clinic opening hours?",
        "ans_ar": "نعم، نعمل قبل الكشف أو بعد إغلاق الاستقبال حسب تعليمات الإدارة",
        "ans_en": "Yes, before clinics open or after reception closes, as management instructs",
    },
    "mall-cleaning": {
        "ar": "تنظيف المجمعات التجارية",
        "en": "mall and commercial cleaning",
        "title_ar": "شركة تنظيف مجمعات تجارية",
        "title_en": "Mall Cleaning",
        "kw_ar": "تنظيف مجمع",
        "method_ar": "ورديات ليلية للممرات، وتنظيف دورات عامة ومواقف، مع تلميع مداخل الرخام",
        "method_en": "Night shifts for corridors, public washrooms and parking, plus polishing of marble entrances",
        "risk_ar": "حركة الزوار في مسقط وصلالة تترك آثار أحذية رملية؛ نضع مداخل رطبة ونكررها في الذروة",
        "risk_en": "Foot traffic in Muscat and Salalah leaves sandy shoe marks; damp entrance mats are refreshed at peak hours",
        "faq_ar": "هل تغطون المحلات أم المشاعات فقط؟",
        "faq_en": "Do you cover shops or only common areas?",
        "ans_ar": "حسب العقد؛ المشاعات أساسية والمحلات باتفاق منفصل مع المستأجر",
        "ans_en": "By contract; common areas are standard and individual shops need a separate tenant agreement",
    },
    "pool-cleaning": {
        "ar": "تنظيف المسابح",
        "en": "swimming pool cleaning",
        "title_ar": "شركة تنظيف مسابح",
        "title_en": "Pool Cleaning",
        "kw_ar": "تنظيف مسبح",
        "method_ar": "فحص الكلور والـ pH، كنس القاع، غسل الفلاتر، وإزالة الطحالب في الظل والرطوبة",
        "method_en": "Chlorine and pH checks, floor vacuuming, filter washing and algae removal in shade and humidity",
        "risk_ar": "غبار عُمان وغبار الخريف في صلالة يرفع الاستهلاك الكيميائي؛ نعاير الجرعة لا نضاعفها عشوائياً",
        "risk_en": "Omani dust and Salalah Khareef debris raise chemical demand; we dose to readings instead of guessing",
        "faq_ar": "هل تشغّلون المضخة بعد التنظيف؟",
        "faq_en": "Do you run the pump after cleaning?",
        "ans_ar": "نعم ونوضح قراءة الماء للعميل قبل المغادرة",
        "ans_en": "Yes, and we show the client the water reading before leaving",
    },
    "kitchen-cleaning": {
        "ar": "تنظيف المطابخ",
        "en": "kitchen cleaning",
        "title_ar": "شركة تنظيف مطابخ",
        "title_en": "Kitchen Cleaning",
        "kw_ar": "تنظيف مطبخ",
        "method_ar": "إزالة الدهون عن الشفاط والأفران، وتعقيم أسطح تقطيع اللحم والسمك الشائعة في البيوت العُمانية",
        "method_en": "Degreasing hoods and ovens, and sanitising meat and fish prep areas common in Omani homes",
        "risk_ar": "البهارات والزيوت تترك طبقة تجذب النمل في الباطنة؛ لا نكتفي بالمسح السطحي",
        "risk_en": "Spices and oils leave a film that attracts ants in Batinah; a surface wipe is not enough",
        "faq_ar": "هل تنظفون داخل الثلاجة؟",
        "faq_en": "Do you clean inside the fridge?",
        "ans_ar": "عند الطلب وبعد إفراغها من العميل، حتى لا نلمس مواد غذائية بدون إذن",
        "ans_en": "On request after the client empties it, so we do not handle food without permission",
    },
    "bathroom-cleaning": {
        "ar": "تنظيف الحمامات",
        "en": "bathroom cleaning",
        "title_ar": "شركة تنظيف حمامات",
        "title_en": "Bathroom Cleaning",
        "kw_ar": "تنظيف حمام",
        "method_ar": "إزالة التكلس عن الخلاطات، وتعقيم المرحاض، وتجفيف الأرض لتفادي الرطوبة الراجعة",
        "method_en": "Descaling taps, sanitising the toilet, and drying floors so humidity does not rebound",
        "risk_ar": "ماء عُمان في بعض المدن يترك كلساً أبيض؛ مواد قوية على الرخام تضرّه فنختار خامة آمنة",
        "risk_en": "Water in some Omani cities leaves white scale; harsh acids damage marble so we choose a safe product",
        "faq_ar": "هل تعالجون العفن حول السيليكون؟",
        "faq_en": "Do you treat mould around silicone?",
        "ans_ar": "نعم سطحياً، وإذا كان السيليكون تالفاً نوصي باستبداله ضمن الصيانة",
        "ans_en": "Yes on the surface; if the silicone has failed we recommend replacement as maintenance",
    },
    "water-tank-cleaning": {
        "ar": "تنظيف خزانات المياه",
        "en": "water tank cleaning",
        "title_ar": "شركة تنظيف خزانات مياه",
        "title_en": "Water Tank Cleaning",
        "kw_ar": "تنظيف خزان مياه",
        "method_ar": "تفريغ آمن، فرك الجدران، شطف، وتعقيم مع تجفيف قبل إعادة التعبئة",
        "method_en": "Safe drain-down, wall scrubbing, rinse and disinfection, then drying before refill",
        "risk_ar": "خزانات الأسطح في عُمان تتعرض لحرارة شديدة وطحالب؛ نعمل في ساعات أبرد ونغلق المصدر أثناء العمل",
        "risk_en": "Roof tanks in Oman face extreme heat and algae; we work in cooler hours and isolate the supply",
        "faq_ar": "كم ساعة ينقطع الماء؟",
        "faq_en": "How long is the water off?",
        "ans_ar": "غالباً نصف يوم لخزان منزلي، ويُحدَّد بعد معرفة السعة وعدد الخزانات",
        "ans_en": "Usually half a day for a domestic tank, confirmed after capacity and tank count",
    },
    "diesel-tank-cleaning": {
        "ar": "تنظيف خزانات الديزل",
        "en": "diesel tank cleaning",
        "title_ar": "شركة تنظيف خزانات ديزل",
        "title_en": "Diesel Tank Cleaning",
        "kw_ar": "تنظيف خزان ديزل",
        "method_ar": "شفط الرواسب، فصل الماء عن الوقود، وتهوية آمنة بعيداً عن اللهب",
        "method_en": "Sludge extraction, water-fuel separation, and safe ventilation away from ignition sources",
        "risk_ar": "الرطوبة الساحلية في مسقط وصور وصحار تزيد تكاثف الماء داخل الخزان؛ نفحص القاع قبل التشغيل",
        "risk_en": "Coastal humidity in Muscat, Sur and Sohar increases water condensation inside tanks; we inspect the sump before restart",
        "faq_ar": "هل تحتاجون تصريحاً للموقع؟",
        "faq_en": "Do you need a site permit?",
        "ans_ar": "للمنشآت نعم حسب إدارة الموقع؛ للخزان المنزلي الصغير يكفي تنسيق السلامة مع العميل",
        "ans_en": "For industrial sites, yes as the facility requires; a small home tank needs a safety briefing with the client",
    },
    "carpet-cleaning": {
        "ar": "تنظيف السجاد",
        "en": "carpet cleaning",
        "title_ar": "شركة تنظيف سجاد",
        "title_en": "Carpet Cleaning",
        "kw_ar": "تنظيف سجاد",
        "method_ar": "سحب غبار جاف أولاً ثم غسل حسب نوع الخيط، وتجفيف سريع حتى لا تبقى رطوبة تحت السجاد",
        "method_en": "Dry soil extraction first, then a wash matched to the fibre, with fast drying so moisture is not trapped underneath",
        "risk_ar": "السجاد العُماني يتعرض لرمل ناعم؛ الغسيل دون سحب أولي يحوّل الرمل إلى طين داخل الوبر",
        "risk_en": "Omani carpets hold fine sand; washing without dry extraction turns that sand into mud inside the pile",
        "faq_ar": "هل تغسلون في الموقع أم تأخذونه؟",
        "faq_en": "Do you clean on site or take the carpet away?",
        "ans_ar": "حسب الحجم والنوع؛ المجالس الكبيرة تُغسل في الموقع مع تجفيف مراوح",
        "ans_en": "It depends on size and type; large majlis pieces are cleaned on site with fan drying",
    },
    "moquette-cleaning": {
        "ar": "تنظيف الموكيت",
        "en": "fitted carpet cleaning",
        "title_ar": "شركة تنظيف موكيت",
        "title_en": "Moquette Cleaning",
        "kw_ar": "تنظيف موكيت",
        "method_ar": "غسيل منخفض الرطوبة للموكيت المثبت حتى لا يتضرر اللاصق في حرارة عُمان",
        "method_en": "Low-moisture cleaning for glued fitted carpet so adhesive does not fail in Omani heat",
        "risk_ar": "الرطوبة العالية في صلالة قد تُبقي الموكيت رطباً ساعات أطول؛ نزيد التجفيف ونؤجل الأثاث الثقيل",
        "risk_en": "High humidity in Salalah keeps fitted carpet damp longer; we extend drying and delay replacing heavy furniture",
        "faq_ar": "هل يبهت اللون؟",
        "faq_en": "Will the colour fade?",
        "ans_ar": "نختبر زاوية مخفية أولاً ونرفض المواد القوية على الموكيت المطبوع",
        "ans_en": "We test a hidden corner first and refuse harsh chemistry on printed pile",
    },
    "sofa-cleaning": {
        "ar": "تنظيف الكنب",
        "en": "sofa cleaning",
        "title_ar": "شركة تنظيف كنب",
        "title_en": "Sofa Cleaning",
        "kw_ar": "تنظيف كنب",
        "method_ar": "تحديد القماش (قماش، جلد، مخمل) ثم بخار أو رغوة جافة، مع إزالة بقع القهوة والتمر",
        "method_en": "Identify the fabric (cloth, leather, velvet) then steam or dry foam, including coffee and date stains",
        "risk_ar": "الكنب في المجالس العُمانية يُستخدم يومياً للضيافة؛ نطلب وقت تجفيف قبل جلوس الضيوف",
        "risk_en": "Sofas in Omani majlis rooms are used daily for guests; we require drying time before seating visitors",
        "faq_ar": "كم قطعة في الزيارة؟",
        "faq_en": "How many pieces per visit?",
        "ans_ar": "يُحسب حسب المقاعد والمساند، ويُكتب في عرض السعر",
        "ans_en": "Counted by seats and cushions, and written on the quote",
    },
    "curtain-cleaning": {
        "ar": "تنظيف الستائر",
        "en": "curtain cleaning",
        "title_ar": "شركة تنظيف ستائر",
        "title_en": "Curtain Cleaning",
        "kw_ar": "تنظيف ستائر",
        "method_ar": "فك بحذر أو غسيل في الموقع للستائر الثابتة، مع إزالة غبار المكيف الملتصق بالقماش",
        "method_en": "Careful take-down or on-site washing for fixed drapes, removing AC dust bonded to the fabric",
        "risk_ar": "الشمس العُمانية تُضعف الأقمشة؛ لا نستخدم حرارة عالية على الستائر المطلة على البحر",
        "risk_en": "Omani sun weakens fabrics; we avoid high heat on seaside curtains",
        "faq_ar": "هل تعيدون التركيب؟",
        "faq_en": "Do you rehang them?",
        "ans_ar": "نعم في نفس الزيارة بعد التأكد من الجفاف حتى لا تُصبغ الجدران",
        "ans_en": "Yes on the same visit after they are dry, so walls are not stained",
    },
    "mattress-cleaning": {
        "ar": "تنظيف المراتب",
        "en": "mattress cleaning",
        "title_ar": "شركة تنظيف مراتب",
        "title_en": "Mattress Cleaning",
        "kw_ar": "تنظيف مرتبة",
        "method_ar": "سحب عميق للغبار والعث، معالجة رطوبة، وتجفيف قبل إعادة الشرشف",
        "method_en": "Deep extraction of dust and mites, moisture treatment, and drying before sheets go back on",
        "risk_ar": "الرطوبة الساحلية تُبقي المرتبة باردة من الداخل؛ نفحص الجانب السفلي لا السطح فقط",
        "risk_en": "Coastal humidity keeps the mattress core cool and damp; we inspect the underside, not only the sleep surface",
        "faq_ar": "هل يمكن النوم عليها مساء الزيارة؟",
        "faq_en": "Can we sleep on it the same night?",
        "ans_ar": "بعد اكتمال الجفاف، وغالباً في نفس اليوم مع مراوح في المناخ الجاف",
        "ans_en": "Once fully dry, often the same day with fans in dry inland weather",
    },
    "marble-polishing": {
        "ar": "جلي وتلميع الرخام",
        "en": "marble polishing",
        "title_ar": "شركة جلي رخام",
        "title_en": "Marble Polishing",
        "kw_ar": "جلي رخام",
        "method_ar": "نفرز الخدوش أولاً، ثم جلي متدرج، ثم طبقة حماية تتحمل الغبار والرطوبة",
        "method_en": "Scratch triage, staged grinding, then a sealer that copes with dust and humidity",
        "risk_ar": "رمل عُمان يخدش الرخام اللامع يومياً عند المداخل؛ نوصي بممسحة ومسار حماية بعد الجلي",
        "risk_en": "Omani grit scratches polished marble at every entrance; we recommend mats and a protection path after polishing",
        "faq_ar": "هل يناسب كل أنواع الرخام العُماني والمستورد؟",
        "faq_en": "Does it suit both Omani and imported marble?",
        "ans_ar": "بعد فحص العيّنة؛ بعض الأحجار المحلية أصلب وتحتاج أقراصاً مختلفة",
        "ans_en": "After inspecting a sample; some local stone is harder and needs different pads",
    },
    "glass-facade-cleaning": {
        "ar": "تنظيف الواجهات الزجاجية",
        "en": "glass facade cleaning",
        "title_ar": "شركة تنظيف واجهات زجاجية",
        "title_en": "Glass Facade Cleaning",
        "kw_ar": "تنظيف واجهات",
        "method_ar": "ماء نقي أو رافعة حسب الارتفاع، مع إزالة أملاح البحر وغبار الصحراء دون خدش",
        "method_en": "Pure water or a lift depending on height, removing sea salt and desert dust without scratching",
        "risk_ar": "الملح في صور ومسقط والندى في صلالة يتركان بقعاً دائمة إن تُركت أياماً في الشمس",
        "risk_en": "Salt in Sur and Muscat and dew in Salalah leave permanent spots if left in the sun for days",
        "faq_ar": "هل تعملون في الرياح؟",
        "faq_en": "Do you work in high wind?",
        "ans_ar": "لا على الارتفاعات؛ نؤجّل لأسباب سلامة وهو أمر شائع على ساحل عُمان",
        "ans_en": "Not at height; we postpone for safety, which is common on the Omani coast",
    },
}

CITY_ORDER = [
    "muscat",
    "salalah",
    "nizwa",
    "sohar",
    "sur",
    "al-buraimi",
    "ibri",
    "rustaq",
]


def related_slugs(service: str, city: str) -> list[tuple[str, str, str]]:
    others = [c for c in CITY_ORDER if c != city]
    out = []
    for slug in others[:4]:
        info = CITIES[slug]
        out.append((f"{service}-{slug}", info["ar"], info["en"]))
    return out


def unique_ar_section(service: str, city: str) -> str:
    c = CITIES[city]
    s = SERVICES[service]
    items = []
    for slug, _ar_name, _en in related_slugs(service, city):
        city_slug = slug[len(service) + 1 :]
        prep = CITIES[city_slug]["prep"]
        items.append(f'<li><a href="/om/{slug}/">{s["title_ar"]} {prep}</a></li>')
    links = "".join(items)
    return f"""<!--rukn-local-start-->
<section class="rukn-oman-local">
<h2>{s["title_ar"]} في {c["ar"]} — خصوصية {c["gov_ar"]}</h2>
<p>ركن التطور يقدّم {s["ar"]} {c["prep"]} داخل {c["gov_ar"]}، لا بنسخ إجراءات مدينة أخرى. {c["note_ar"]}. طبيعة المكان هنا: {c["climate_ar"]}. المباني الشائعة: {c["stock_ar"]}.</p>
<p>{s["method_ar"]}. {s["risk_ar"]}. التغطية الميدانية تشمل: {c["areas_ar"]}. السعر يُكتب بالريال العُماني بعد المعاينة، وليس تقديراً هاتفياً ولا بعملة دولة أخرى.</p>
<h3>أحياء ومناطق نخدمها في {c["ar"]}</h3>
<p>{c["areas_ar"]}.</p>
<h3>{s["faq_ar"]}</h3>
<p>{s["ans_ar"]} في {c["ar"]}.</p>
<h3>خدمات مشابهة في مدن عُمانية أخرى</h3>
<ul>{links}</ul>
<p>لطلب {s["kw_ar"]} {c["prep"]} راسلنا واتساب لتحديد موعد فريق مقيم في السلطنة.</p>
</section>
<!--rukn-local-end-->"""


def unique_en_article(service: str, city: str, ar_title: str) -> dict[str, str]:
    c = CITIES[city]
    s = SERVICES[service]
    title = f"{s['title_en']} in {c['en']}, Oman"
    desc = (
        f"{s['title_en']} in {c['en']} ({c['gov_en']}): {c['climate_en']}. "
        f"Rukn Eltatawer surveys the site and issues a written quote in OMR."
    )[:160]
    items = []
    for slug, _ar, en_name in related_slugs(service, city):
        items.append(f'<li><a href="/om/en/{slug}/">{s["title_en"]} in {en_name}</a></li>')
    html = f"""<section>
<h2>{title} — local guide</h2>
<p>Rukn Eltatawer provides {s['en']} in {c['en']}, {c['gov_en']}, Sultanate of Oman. {c['note_en']}. Local conditions: {c['climate_en']}. Building stock: {c['stock_en']}.</p>
<p>{s['method_en']}. {s['risk_en']}. Neighbourhoods we cover include {c['areas_en']}. Pricing is in Omani rial after an on-site visit — not a phone guess and not UAE dirham.</p>
<h3>Areas in {c['en']}</h3>
<p>{c['areas_en']}.</p>
<h3>{s['faq_en']}</h3>
<p>{s['ans_en']} in {c['en']}.</p>
<h3>Same service in other Oman cities</h3>
<ul>{''.join(items)}</ul>
<p>Arabic page: <a href="/om/{service}-{city}/">{ar_title}</a>. WhatsApp the Oman team to book a survey.</p>
</section>"""
    excerpt = f"{s['title_en']} in {c['en']}, Oman. On-site survey, written OMR quote, crew familiar with {c['gov_en']}."
    return {"title": title, "desc": desc, "html": html, "excerpt": excerpt}


def unique_intro_ar(service: str, city: str) -> str:
    c = CITIES[city]
    s = SERVICES[service]
    return (
        f"<p>خدمة {s['ar']} {c['prep']} من ركن التطور مصممة لـ{c['gov_ar']}: "
        f"{c['climate_ar']}. {s['method_ar']}. نعمل في {c['areas_ar']}، "
        f"والمعاينة قبل أي سعر بالريال العُماني.</p>"
    )


def english_home_html() -> str:
    city_links = "".join(
        f'<li><a href="/om/en/home-cleaning-{slug}/">House cleaning in {info["en"]}</a> — {info["gov_en"]}</li>'
        for slug, info in CITIES.items()
    )
    service_links = "".join(
        f'<li><a href="/om/en/{svc}-muscat/">{meta["title_en"]} in Muscat</a></li>'
        for svc, meta in SERVICES.items()
    )
    return f"""<section>
<h2>Home services in the Sultanate of Oman</h2>
<p>Rukn Eltatawer Oman is a field team for cleaning, leak detection, roof insulation, plumbing, AC and general maintenance. We work in Muscat, Salalah, Nizwa, Sohar, Sur, Al Buraimi, Ibri and Rustaq. Quotes are written in Omani rial after a site visit.</p>
<p>This English section is for residents and companies who prefer English. The Arabic site remains the main local version. Both versions describe the same Oman operation — not a copy of a UAE emirate page.</p>
<h3>Cities we cover</h3>
<ul>{city_links}</ul>
<h3>Cleaning services (Muscat English guides)</h3>
<ul>{service_links}</ul>
<p>Call or WhatsApp the number on this page to book a survey. We do not price complex work by phone.</p>
</section>"""
