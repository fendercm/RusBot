"""Учебный контент RusBot"""

# Переводы интерфейса
TRANSLATIONS = {
    "en": {
        "welcome": "🇷🇺 Welcome to RusBot!\n\nI'm your personal Russian language tutor.\nPlease choose your interface language:",
        "language_set": "✅ Language set to English!",
        "choose_level": "📊 Now let's determine your Russian level.\nPlease take a short placement test (5 questions):",
        "main_menu": "🏠 Main Menu",
        "start_quiz": "📝 Start Daily Quiz",
        "my_progress": "📈 My Progress",
        "leaderboard": "🏆 Leaderboard",
        "settings": "⚙️ Settings",
        "grammar": "📚 Grammar",
        "vocabulary": "📖 Vocabulary",
        "back": "◀️ Back",
        "correct": "✅ Correct! +{xp} XP",
        "wrong": "❌ Wrong! The correct answer: {answer}",
        "next": "➡️ Next",
        "finish": "🏁 Finish",
        "quiz_result": "📊 Quiz Result:\n✅ Correct: {correct}/{total}\n⭐ XP earned: +{xp}",
        "level_label": "Level",
        "xp_label": "XP",
        "streak_label": "🔥 Streak",
        "rank_label": "🏅 Rank",
        "days_label": "days",
    },
    "zh": {
        "welcome": "🇷🇺 欢迎来到RusBot！\n\n我是您的俄语私人导师。\n请选择界面语言：",
        "language_set": "✅ 语言设置为中文！",
        "choose_level": "📊 现在让我们确定您的俄语水平。\n请参加简短的定级测试（5道题）：",
        "main_menu": "🏠 主菜单",
        "start_quiz": "📝 开始每日测验",
        "my_progress": "📈 我的进度",
        "leaderboard": "🏆 排行榜",
        "settings": "⚙️ 设置",
        "grammar": "📚 语法",
        "vocabulary": "📖 词汇",
        "back": "◀️ 返回",
        "correct": "✅ 正确！+{xp} XP",
        "wrong": "❌ 错误！正确答案：{answer}",
        "next": "➡️ 下一题",
        "finish": "🏁 完成",
        "quiz_result": "📊 测验结果：\n✅ 正确：{correct}/{total}\n⭐ 获得XP：+{xp}",
        "level_label": "级别",
        "xp_label": "经验值",
        "streak_label": "🔥 连续天数",
        "rank_label": "🏅 排名",
        "days_label": "天",
    },
    "ar": {
        "welcome": "🇷🇺 مرحباً بك في RusBot!\n\nأنا مدرسك الشخصي للغة الروسية.\nيرجى اختيار لغة الواجهة:",
        "language_set": "✅ تم ضبط اللغة على العربية!",
        "choose_level": "📊 الآن دعنا نحدد مستوى الروسية لديك.\nيرجى إجراء اختبار تحديد المستوى (5 أسئلة):",
        "main_menu": "🏠 القائمة الرئيسية",
        "start_quiz": "📝 بدء الاختبار اليومي",
        "my_progress": "📈 تقدمي",
        "leaderboard": "🏆 لوحة المتصدرين",
        "settings": "⚙️ الإعدادات",
        "grammar": "📚 القواعد",
        "vocabulary": "📖 المفردات",
        "back": "◀️ رجوع",
        "correct": "✅ صحيح! +{xp} XP",
        "wrong": "❌ خطأ! الإجابة الصحيحة: {answer}",
        "next": "➡️ التالي",
        "finish": "🏁 إنهاء",
        "quiz_result": "📊 نتيجة الاختبار:\n✅ صحيح: {correct}/{total}\n⭐ XP المكتسب: +{xp}",
        "level_label": "المستوى",
        "xp_label": "نقاط الخبرة",
        "streak_label": "🔥 سلسلة الأيام",
        "rank_label": "🏅 الترتيب",
        "days_label": "أيام",
    },
    "es": {
        "welcome": "🇷🇺 ¡Bienvenido a RusBot!\n\nSoy tu tutor personal de ruso.\nPor favor, elige el idioma de la interfaz:",
        "language_set": "✅ ¡Idioma establecido en español!",
        "choose_level": "📊 Ahora determinemos tu nivel de ruso.\nRealiza una prueba de ubicación rápida (5 preguntas):",
        "main_menu": "🏠 Menú Principal",
        "start_quiz": "📝 Iniciar Quiz Diario",
        "my_progress": "📈 Mi Progreso",
        "leaderboard": "🏆 Clasificación",
        "settings": "⚙️ Configuración",
        "grammar": "📚 Gramática",
        "vocabulary": "📖 Vocabulario",
        "back": "◀️ Atrás",
        "correct": "✅ ¡Correcto! +{xp} XP",
        "wrong": "❌ ¡Incorrecto! La respuesta correcta: {answer}",
        "next": "➡️ Siguiente",
        "finish": "🏁 Terminar",
        "quiz_result": "📊 Resultado del Quiz:\n✅ Correctas: {correct}/{total}\n⭐ XP ganados: +{xp}",
        "level_label": "Nivel",
        "xp_label": "XP",
        "streak_label": "🔥 Racha",
        "rank_label": "🏅 Posición",
        "days_label": "días",
    }
}

def t(lang: str, key: str, **kwargs) -> str:
    """Получить перевод"""
    lang = lang if lang in TRANSLATIONS else "en"
    text = TRANSLATIONS[lang].get(key, TRANSLATIONS["en"].get(key, key))
    if kwargs:
        text = text.format(**kwargs)
    return text

# ===== PLACEMENT TEST =====
PLACEMENT_TEST = [
    {
        "question": "Как тебя зовут? Меня зовут ...",
        "options": ["Иван", "Ивана", "Иваном", "Иване"],
        "correct": 0,
        "level": "A1",
        "explanation": {
            "en": "After 'зовут' we use Nominative case (Именительный падеж). The name stays unchanged.",
            "zh": "'зовут'后面使用主格（именительный падеж）。名字保持不变。",
            "ar": "بعد 'зовут' نستخدم حالة الاسم (الإسمية). يبقى الاسم دون تغيير.",
            "es": "Después de 'зовут' usamos el caso Nominativo. El nombre no cambia."
        }
    },
    {
        "question": "Я живу ... Москве.",
        "options": ["в", "на", "из", "у"],
        "correct": 0,
        "level": "A1",
        "explanation": {
            "en": "We use 'в' (in) with cities: в Москве, в Лондоне, в Пекине.",
            "zh": "城市前使用'в'（在）：в Москве, в Лондоне。",
            "ar": "نستخدم 'в' (في) مع المدن: в Москве، в Лондоне.",
            "es": "Usamos 'в' (en) con ciudades: в Москве, в Лондоне."
        }
    },
    {
        "question": "Это книга ... студента.",
        "options": ["Именительный", "Родительный", "Дательный", "Творительный"],
        "correct": 1,
        "level": "A2",
        "explanation": {
            "en": "After a noun showing possession we use Genitive case (Родительный падеж): книга студента = student's book.",
            "zh": "表示所属关系时使用属格（родительный падеж）：книга студента = 学生的书。",
            "ar": "للدلالة على الملكية نستخدم حالة الملكية (Родительный): книга студента = كتاب الطالب.",
            "es": "Para indicar posesión usamos el Genitivo: книга студента = el libro del estudiante."
        }
    },
    {
        "question": "Он ... в библиотеку каждый день.",
        "options": ["идёт", "едет", "ходит", "ездит"],
        "correct": 2,
        "level": "B1",
        "explanation": {
            "en": "For habitual/repeated action on foot we use 'ходить' (multidirectional). 'Идти' = going right now.",
            "zh": "表示习惯性步行动作用'ходить'（多向动词）。'Идти' = 正在走。",
            "ar": "للحركة المعتادة/المتكررة سيرًا على الأقدام نستخدم 'ходить'. 'Идти' = يذهب الآن.",
            "es": "Para acción habitual a pie usamos 'ходить'. 'Идти' = va ahora mismo."
        }
    },
    {
        "question": "Если бы я ... время, я бы выучил русский язык.",
        "options": ["имею", "имел", "буду иметь", "имел бы"],
        "correct": 1,
        "level": "B2",
        "explanation": {
            "en": "Conditional mood in Russian: 'если бы + past tense'. 'Если бы я имел...' = 'If I had...'",
            "zh": "俄语条件句：'если бы + 过去时'。'Если бы я имел...' = '如果我有...'",
            "ar": "المزاج الشرطي بالروسية: 'если бы + الماضي'. 'Если бы я имел...' = 'لو كان لديّ...'",
            "es": "Condicional en ruso: 'если бы + pasado'. 'Если бы я имел...' = 'Si yo tuviera...'"
        }
    }
]

# ===== DAILY QUIZZES =====
DAILY_QUIZZES = {
    "A1": [
        {
            "question": "Переведите: «Это стол»",
            "options": ["This is a table", "This is a chair", "This is a door", "This is a window"],
            "correct": 0,
            "xp": 10,
            "topic": "vocabulary"
        },
        {
            "question": "Какой падеж? «Я вижу дом»",
            "options": ["Именительный", "Винительный", "Родительный", "Дательный"],
            "correct": 1,
            "xp": 15,
            "topic": "grammar"
        },
        {
            "question": "Это ... книга. (my)",
            "options": ["моя", "мой", "моё", "мои"],
            "correct": 0,
            "xp": 10,
            "topic": "grammar"
        },
        {
            "question": "Как сказать «Hello» по-русски?",
            "options": ["Пока", "Привет", "Спасибо", "Пожалуйста"],
            "correct": 1,
            "xp": 5,
            "topic": "vocabulary"
        },
        {
            "question": "Выберите правильный вариант: «Я ... студент»",
            "options": ["есть", "—", "быть", "является"],
            "correct": 1,
            "xp": 10,
            "topic": "grammar"
        },
    ],
    "A2": [
        {
            "question": "Где живёт Анна? Анна живёт ... России.",
            "options": ["в", "на", "из", "по"],
            "correct": 0,
            "xp": 10,
            "topic": "grammar"
        },
        {
            "question": "Правильная форма: «Я хочу ... кофе»",
            "options": ["пить", "выпить", "пью", "выпью"],
            "correct": 1,
            "xp": 15,
            "topic": "grammar"
        },
        {
            "question": "Переведите: «красивый город»",
            "options": ["beautiful city", "big city", "old city", "new city"],
            "correct": 0,
            "xp": 10,
            "topic": "vocabulary"
        },
        {
            "question": "Мне ... 20 лет. (to be / is)",
            "options": ["есть", "—", "было", "будет"],
            "correct": 1,
            "xp": 15,
            "topic": "grammar"
        },
        {
            "question": "Антоним слова «большой»:",
            "options": ["маленький", "красивый", "новый", "старый"],
            "correct": 0,
            "xp": 10,
            "topic": "vocabulary"
        },
    ],
    "B1": [
        {
            "question": "Глагол движения: Каждое утро я ... на работу пешком.",
            "options": ["иду", "хожу", "еду", "езжу"],
            "correct": 1,
            "xp": 20,
            "topic": "grammar"
        },
        {
            "question": "Совершенный вид: «Я ... письмо вчера.»",
            "options": ["писал", "написал", "пишу", "напишу"],
            "correct": 1,
            "xp": 20,
            "topic": "grammar"
        },
        {
            "question": "Падеж после «без»:",
            "options": ["Именительный", "Родительный", "Дательный", "Творительный"],
            "correct": 1,
            "xp": 15,
            "topic": "grammar"
        },
        {
            "question": "Вставьте: «Он работает ... врач»",
            "options": ["как", "в качестве", "врачом", "врача"],
            "correct": 2,
            "xp": 20,
            "topic": "grammar"
        },
        {
            "question": "Деепричастие от «читать»:",
            "options": ["читая", "читав", "читающий", "прочитав"],
            "correct": 0,
            "xp": 25,
            "topic": "grammar"
        },
    ],
    "B2": [
        {
            "question": "Если бы он ... раньше, мы бы успели.",
            "options": ["пришёл", "придёт", "приходит", "приходил"],
            "correct": 0,
            "xp": 25,
            "topic": "grammar"
        },
        {
            "question": "Синоним слова «осуществить»:",
            "options": ["реализовать", "найти", "потерять", "избежать"],
            "correct": 0,
            "xp": 20,
            "topic": "vocabulary"
        },
        {
            "question": "Страдательный залог: «Книга ... студентом»",
            "options": ["читает", "читается", "читала", "была прочитана"],
            "correct": 3,
            "xp": 30,
            "topic": "grammar"
        },
        {
            "question": "Правильная форма причастия: «человек, ... книгу»",
            "options": ["читающий", "читавший", "прочитавший", "читаемый"],
            "correct": 0,
            "xp": 25,
            "topic": "grammar"
        },
        {
            "question": "Фразеологизм «бить баклуши» означает:",
            "options": ["бездельничать", "работать", "учиться", "путешествовать"],
            "correct": 0,
            "xp": 20,
            "topic": "vocabulary"
        },
    ]
}

# ===== GRAMMAR LESSONS =====
GRAMMAR_LESSONS = {
    "cases": {
        "title": "📚 Падежная система русского языка",
        "content": {
            "en": """
🔤 *Russian Case System*

Russian has 6 cases. Here's a quick guide:

1️⃣ *Nominative (Именительный)* — Subject
   • Кто? Что? | Who? What?
   • _Студент читает книгу._

2️⃣ *Genitive (Родительный)* — Possession, absence
   • Кого? Чего? | Of whom? Of what?
   • _Книга студента. Нет времени._

3️⃣ *Dative (Дательный)* — Indirect object
   • Кому? Чему? | To whom?
   • _Я даю книгу студенту._

4️⃣ *Accusative (Винительный)* — Direct object
   • Кого? Что? | Whom? What?
   • _Я вижу студента._

5️⃣ *Instrumental (Творительный)* — By, with
   • Кем? Чем? | By whom? With what?
   • _Он работает врачом._

6️⃣ *Prepositional (Предложный)* — Location, about
   • О ком? О чём? | About whom?
   • _Я думаю о студенте._
""",
            "zh": """
🔤 *俄语格系统*

俄语有6个格。简要说明：

1️⃣ *主格 (Именительный)* — 主语
   • 谁？什么？
   • _Студент читает книгу._（学生在读书）

2️⃣ *属格 (Родительный)* — 所属、缺失
   • 谁的？什么的？
   • _Книга студента._ （学生的书）

3️⃣ *与格 (Дательный)* — 间接宾语
   • 给谁？给什么？
   • _Я даю книгу студенту._ （我给学生书）

4️⃣ *宾格 (Винительный)* — 直接宾语
   • 谁？什么？
   • _Я вижу студента._ （我看见学生）

5️⃣ *工具格 (Творительный)* — 用、以、作为
   • 由谁？用什么？
   • _Он работает врачом._ （他当医生）

6️⃣ *前置格 (Предложный)* — 位置、关于
   • 关于谁？关于什么？
   • _Я думаю о студенте._ （我在想学生）
""",
            "ar": """
🔤 *نظام الحالات الإعرابية في الروسية*

للغة الروسية 6 حالات إعرابية:

1️⃣ *الحالة الاسمية (Именительный)* — الفاعل
   • من؟ ماذا؟
   • _Студент читает книгу._ (الطالب يقرأ كتابًا)

2️⃣ *حالة الملكية (Родительный)* — الملكية، الغياب
   • لمن؟ لماذا؟
   • _Книга студента._ (كتاب الطالب)

3️⃣ *حالة الإضافة (Дательный)* — المفعول غير المباشر
   • لمن؟
   • _Я даю книгу студенту._ (أعطي الطالب كتابًا)

4️⃣ *حالة المفعول به (Винительный)* — المفعول المباشر
   • _Я вижу студента._ (أرى الطالب)

5️⃣ *حالة الأداة (Творительный)* — بواسطة، مع
   • _Он работает врачом._ (يعمل طبيبًا)

6️⃣ *حالة الجر (Предложный)* — الموقع، عن
   • _Я думаю о студенте._ (أفكر في الطالب)
""",
            "es": """
🔤 *Sistema de Casos del Ruso*

El ruso tiene 6 casos:

1️⃣ *Nominativo (Именительный)* — Sujeto
   • ¿Quién? ¿Qué?
   • _Студент читает книгу._ (El estudiante lee el libro)

2️⃣ *Genitivo (Родительный)* — Posesión, ausencia
   • ¿De quién? ¿De qué?
   • _Книга студента._ (El libro del estudiante)

3️⃣ *Dativo (Дательный)* — Objeto indirecto
   • ¿A quién?
   • _Я даю книгу студенту._ (Doy el libro al estudiante)

4️⃣ *Acusativo (Винительный)* — Objeto directo
   • _Я вижу студента._ (Veo al estudiante)

5️⃣ *Instrumental (Творительный)* — Por, con
   • _Он работает врачом._ (Trabaja como médico)

6️⃣ *Preposicional (Предложный)* — Lugar, sobre
   • _Я думаю о студенте._ (Pienso en el estudiante)
"""
        }
    },
    "verbs_of_motion": {
        "title": "🚶 Глаголы движения",
        "content": {
            "en": """
🚶 *Verbs of Motion*

The key distinction: *unidirectional* vs *multidirectional*

| Action | Uni (now/one way) | Multi (habit/round trip) |
|--------|-------------------|--------------------------|
| Walk   | идти              | ходить                   |
| Ride   | ехать             | ездить                   |
| Fly    | лететь            | летать                   |
| Run    | бежать            | бегать                   |

📌 *Rules:*
• _Сейчас я иду в магазин._ — going now (one direction)
• _Я хожу в магазин каждый день._ — go regularly
• _Завтра я еду в Москву._ — going to Moscow (one-time)
• _Я часто езжу в Москву._ — go to Moscow often
""",
            "zh": """
🚶 *运动动词*

关键区别：*单向*vs*多向*

| 动作 | 单向（现在/一次） | 多向（习惯/来回） |
|------|-----------------|-----------------|
| 步行 | идти            | ходить          |
| 乘坐 | ехать           | ездить          |
| 飞行 | лететь          | летать          |
| 跑步 | бежать          | бегать          |

📌 *规则：*
• _Сейчас я иду в магазин._ — 正在去（单向）
• _Я хожу в магазин каждый день._ — 每天去
• _Завтра я еду в Москву._ — 明天去莫斯科（一次）
• _Я часто езжу в Москву._ — 经常去莫斯科
""",
            "ar": """
🚶 *أفعال الحركة*

الفرق الأساسي: *أحادي الاتجاه* مقابل *متعدد الاتجاهات*

| الفعل | أحادي (الآن/مرة) | متعدد (عادة/ذهاب وإياب) |
|-------|-----------------|------------------------|
| المشي | идти            | ходить                 |
| الركوب | ехать          | ездить                 |
| الطيران | лететь        | летать                 |
| الجري | бежать          | бегать                 |

📌 *القواعد:*
• _Сейчас я иду в магазин._ — أذهب الآن
• _Я хожу в магазин каждый день._ — أذهب كل يوم
""",
            "es": """
🚶 *Verbos de Movimiento*

La distinción clave: *unidireccional* vs *multidireccional*

| Acción  | Uni (ahora/una vez) | Multi (hábito/ida y vuelta) |
|---------|--------------------|-----------------------------|
| Caminar | идти               | ходить                      |
| Ir (veh)| ехать              | ездить                      |
| Volar   | лететь             | летать                      |
| Correr  | бежать             | бегать                      |

📌 *Reglas:*
• _Сейчас я иду в магазин._ — voy ahora
• _Я хожу в магазин каждый день._ — voy todos los días
"""
        }
    }
}

# Словарь: уровень -> следующий
LEVEL_PROGRESSION = {
    "A1": "A2",
    "A2": "B1",
    "B1": "B2",
    "B2": "B2"
}

def determine_level_from_score(score: int, total: int) -> str:
    """Определить уровень по результату теста"""
    percent = score / total
    if percent < 0.4:
        return "A1"
    elif percent < 0.6:
        return "A2"
    elif percent < 0.8:
        return "B1"
    else:
        return "B2"