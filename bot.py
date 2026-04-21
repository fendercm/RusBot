import asyncio
import logging
import random
from os import getenv
from datetime import date

import aiosqlite
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = getenv("BOT_TOKEN")
DB_PATH = "rusbot.db"

# ============================================================
# DATABASE
# ============================================================

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                language TEXT DEFAULT 'en',
                level TEXT DEFAULT 'A1',
                xp INTEGER DEFAULT 0,
                streak INTEGER DEFAULT 0,
                last_activity TEXT,
                placement_done INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                topic TEXT,
                correct INTEGER,
                total INTEGER,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id=?", (user_id,)) as cur:
            return await cur.fetchone()

async def create_user(user_id, username, full_name):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id,username,full_name) VALUES (?,?,?)",
            (user_id, username, full_name)
        )
        await db.commit()

async def update_user(user_id, **kwargs):
    if not kwargs:
        return
    fields = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [user_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE users SET {fields} WHERE user_id=?", vals)
        await db.commit()

async def add_xp(user_id, amount):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET xp=xp+? WHERE user_id=?", (amount, user_id))
        await db.commit()

async def update_streak(user_id):
    user = await get_user(user_id)
    if not user:
        return
    today = str(date.today())
    last = user["last_activity"]
    async with aiosqlite.connect(DB_PATH) as db:
        if not last:
            await db.execute(
                "UPDATE users SET streak=1, last_activity=? WHERE user_id=?",
                (today, user_id)
            )
        else:
            from datetime import datetime
            last_date = datetime.fromisoformat(last).date() if 'T' in last else date.fromisoformat(last)
            diff = (date.today() - last_date).days
            if diff == 1:
                await db.execute(
                    "UPDATE users SET streak=streak+1, last_activity=? WHERE user_id=?",
                    (today, user_id)
                )
            elif diff > 1:
                await db.execute(
                    "UPDATE users SET streak=1, last_activity=? WHERE user_id=?",
                    (today, user_id)
                )
        await db.commit()

async def save_quiz_result(user_id, topic, correct, total):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO quiz_results (user_id,topic,correct,total) VALUES (?,?,?,?)",
            (user_id, topic, correct, total)
        )
        await db.commit()

async def get_leaderboard(limit=10):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT user_id,full_name,username,xp,level,streak FROM users ORDER BY xp DESC LIMIT ?",
            (limit,)
        ) as cur:
            return await cur.fetchall()

async def get_user_rank(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*)+1 FROM users WHERE xp>(SELECT xp FROM users WHERE user_id=?)",
            (user_id,)
        ) as cur:
            row = await cur.fetchone()
            return row[0] if row else 1

async def get_user_stats(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT COUNT(*) as tq, SUM(correct) as tc, SUM(total) as tt FROM quiz_results WHERE user_id=?",
            (user_id,)
        ) as cur:
            return await cur.fetchone()

# ============================================================
# CONTENT
# ============================================================

LANG_NAMES = {"en": "🇬🇧 English", "zh": "🇨🇳 中文", "ar": "🇸🇦 العربية", "es": "🇪🇸 Español"}

TEXTS = {
    "en": {
        "btn_quiz": "📝 Start Daily Quiz",
        "btn_progress": "📈 My Progress",
        "btn_leaderboard": "🏆 Leaderboard",
        "btn_grammar": "📚 Grammar",
        "btn_vocabulary": "📖 Vocabulary",
        "btn_settings": "⚙️ Settings",
        "btn_back": "◀️ Back to Menu",
        "correct": "✅ Correct! +{xp} XP",
        "wrong": "❌ Wrong! Correct answer: {ans}",
        "next": "➡️ Next",
        "finish": "🏁 Finish",
        "menu": "🏠 Main Menu",
    },
    "zh": {
        "btn_quiz": "📝 开始每日测验",
        "btn_progress": "📈 我的进度",
        "btn_leaderboard": "🏆 排行榜",
        "btn_grammar": "📚 语法",
        "btn_vocabulary": "📖 词汇",
        "btn_settings": "⚙️ 设置",
        "btn_back": "◀️ 返回菜单",
        "correct": "✅ 正确！+{xp} XP",
        "wrong": "❌ 错误！正确答案：{ans}",
        "next": "➡️ 下一题",
        "finish": "🏁 完成",
        "menu": "🏠 主菜单",
    },
    "ar": {
        "btn_quiz": "📝 بدء الاختبار اليومي",
        "btn_progress": "📈 تقدمي",
        "btn_leaderboard": "🏆 لوحة المتصدرين",
        "btn_grammar": "📚 القواعد",
        "btn_vocabulary": "📖 المفردات",
        "btn_settings": "⚙️ الإعدادات",
        "btn_back": "◀️ العودة للقائمة",
        "correct": "✅ صحيح! +{xp} XP",
        "wrong": "❌ خطأ! الإجابة الصحيحة: {ans}",
        "next": "➡️ التالي",
        "finish": "🏁 إنهاء",
        "menu": "🏠 القائمة الرئيسية",
    },
    "es": {
        "btn_quiz": "📝 Iniciar Quiz Diario",
        "btn_progress": "📈 Mi Progreso",
        "btn_leaderboard": "🏆 Clasificación",
        "btn_grammar": "📚 Gramática",
        "btn_vocabulary": "📖 Vocabulario",
        "btn_settings": "⚙️ Configuración",
        "btn_back": "◀️ Volver al Menú",
        "correct": "✅ ¡Correcto! +{xp} XP",
        "wrong": "❌ ¡Incorrecto! Respuesta correcta: {ans}",
        "next": "➡️ Siguiente",
        "finish": "🏁 Terminar",
        "menu": "🏠 Menú Principal",
    },
}

def tx(lang, key, **kw):
    lang = lang if lang in TEXTS else "en"
    s = TEXTS[lang].get(key, TEXTS["en"].get(key, key))
    return s.format(**kw) if kw else s

PLACEMENT_TEST = [
    {
        "q": "Как тебя зовут? Меня зовут ...",
        "opts": ["Иван", "Ивана", "Иваном", "Иване"],
        "ans": 0,
        "exp": {
            "en": "After 'зовут' we use Nominative case. The name stays unchanged.",
            "zh": "'зовут'后面使用主格。名字保持不变。",
            "ar": "بعد 'зовут' نستخدم حالة الاسم الإسمية.",
            "es": "Después de 'зовут' usamos el Nominativo."
        }
    },
    {
        "q": "Я живу ... Москве.",
        "opts": ["в", "на", "из", "у"],
        "ans": 0,
        "exp": {
            "en": "We use 'в' (in) with cities: в Москве, в Лондоне.",
            "zh": "城市前使用'в'：в Москве。",
            "ar": "نستخدم 'в' مع المدن.",
            "es": "Usamos 'в' (en) con ciudades."
        }
    },
    {
        "q": "Это книга ... студента.",
        "opts": ["Именительный", "Родительный", "Дательный", "Творительный"],
        "ans": 1,
        "exp": {
            "en": "Possession uses Genitive case: книга студента = student's book.",
            "zh": "表示所属用属格：книга студента。",
            "ar": "للملكية نستخدم حالة الملكية.",
            "es": "La posesión usa Genitivo: книга студента."
        }
    },
    {
        "q": "Он ... в библиотеку каждый день.",
        "opts": ["идёт", "едет", "ходит", "ездит"],
        "ans": 2,
        "exp": {
            "en": "Habitual action on foot → ходить (multidirectional). Идти = going right now.",
            "zh": "习惯性步行用ходить（多向）。идти=正在走。",
            "ar": "للحركة المعتادة نستخدم ходить.",
            "es": "Acción habitual a pie → ходить."
        }
    },
    {
        "q": "Если бы я ... время, я бы выучил русский.",
        "opts": ["имею", "имел", "буду иметь", "имел бы"],
        "ans": 1,
        "exp": {
            "en": "Conditional: если бы + past tense. 'If I had...'",
            "zh": "条件句：если бы + 过去时。",
            "ar": "الشرطي: если бы + الماضي.",
            "es": "Condicional: если бы + pasado."
        }
    }
]

DAILY_QUIZZES = {
    "A1": [
        {"q": "Переведите: «стол»", "opts": ["table", "chair", "door", "window"], "ans": 0, "xp": 10},
        {"q": "Это ... книга. (my)", "opts": ["моя", "мой", "моё", "мои"], "ans": 0, "xp": 10},
        {"q": "Как сказать «Hello»?", "opts": ["Пока", "Привет", "Спасибо", "Пожалуйста"], "ans": 1, "xp": 5},
        {"q": "Какой падеж? «Я вижу дом»", "opts": ["Именительный", "Винительный", "Родительный", "Дательный"], "ans": 1, "xp": 15},
        {"q": "Переведите: «большой»", "opts": ["big", "small", "new", "old"], "ans": 0, "xp": 10},
        {"q": "Я ... студент. (правильный вариант)", "opts": ["есть", "—", "быть", "является"], "ans": 1, "xp": 10},
        {"q": "Переведите: «спасибо»", "opts": ["please", "hello", "thank you", "goodbye"], "ans": 2, "xp": 5},
    ],
    "A2": [
        {"q": "Анна живёт ... России.", "opts": ["в", "на", "из", "по"], "ans": 0, "xp": 10},
        {"q": "Я хочу ... кофе (сов. вид)", "opts": ["пить", "выпить", "пью", "выпью"], "ans": 1, "xp": 15},
        {"q": "Мне ... 20 лет.", "opts": ["есть", "—", "было", "будет"], "ans": 1, "xp": 15},
        {"q": "Антоним: «большой»", "opts": ["маленький", "красивый", "новый", "старый"], "ans": 0, "xp": 10},
        {"q": "Переведите: «красивый»", "opts": ["beautiful", "big", "old", "new"], "ans": 0, "xp": 10},
        {"q": "Падеж после предлога «в» (место)", "opts": ["Именительный", "Предложный", "Родительный", "Дательный"], "ans": 1, "xp": 15},
        {"q": "Форма мн. числа: «студент»", "opts": ["студенты", "студентов", "студентам", "студентами"], "ans": 0, "xp": 10},
    ],
    "B1": [
        {"q": "Каждое утро я ... на работу пешком.", "opts": ["иду", "хожу", "еду", "езжу"], "ans": 1, "xp": 20},
        {"q": "Я ... письмо вчера. (сов. вид)", "opts": ["писал", "написал", "пишу", "напишу"], "ans": 1, "xp": 20},
        {"q": "Падеж после «без»", "opts": ["Именительный", "Родительный", "Дательный", "Творительный"], "ans": 1, "xp": 15},
        {"q": "Он работает ... врач.", "opts": ["как", "в качестве", "врачом", "врача"], "ans": 2, "xp": 20},
        {"q": "Деепричастие от «читать» (НСВ)", "opts": ["читая", "читав", "читающий", "прочитав"], "ans": 0, "xp": 25},
        {"q": "Вид глагола: «прочитать»", "opts": ["НСВ", "СВ", "оба вида", "нет вида"], "ans": 1, "xp": 15},
        {"q": "Причастие: «студент, ... книгу сейчас»", "opts": ["читающий", "читавший", "прочитавший", "читаемый"], "ans": 0, "xp": 20},
    ],
    "B2": [
        {"q": "Если бы он ... раньше, мы бы успели.", "opts": ["пришёл", "придёт", "приходит", "приходил"], "ans": 0, "xp": 25},
        {"q": "Синоним: «осуществить»", "opts": ["реализовать", "найти", "потерять", "избежать"], "ans": 0, "xp": 20},
        {"q": "«Книга ... студентом» — страд. залог прош.", "opts": ["читает", "читается", "читала", "была прочитана"], "ans": 3, "xp": 30},
        {"q": "Фразеологизм «бить баклуши»:", "opts": ["бездельничать", "работать", "учиться", "путешествовать"], "ans": 0, "xp": 20},
        {"q": "Синоним: «тем не менее»", "opts": ["однако", "поэтому", "например", "иначе"], "ans": 0, "xp": 25},
        {"q": "Управление: «согласно» + ...", "opts": ["Дат. падеж", "Род. падеж", "Тв. падеж", "Вин. падеж"], "ans": 0, "xp": 25},
        {"q": "«Несмотря на» — это:", "opts": ["производный предлог", "союз", "частица", "наречие"], "ans": 0, "xp": 20},
    ],
}

GRAMMAR_TOPICS = {
    "cases": {
        "title": "📝 Падежная система",
        "en": (
            "*Russian Cases (Падежи)*\n\n"
            "1️⃣ *Nominative* — Subject. Кто? Что?\n"
            "   _Студент читает._\n\n"
            "2️⃣ *Genitive* — Possession. Кого? Чего?\n"
            "   _Книга студента._\n\n"
            "3️⃣ *Dative* — To whom. Кому?\n"
            "   _Дать книгу студенту._\n\n"
            "4️⃣ *Accusative* — Object. Кого? Что?\n"
            "   _Вижу студента._\n\n"
            "5️⃣ *Instrumental* — With/by. Кем? Чем?\n"
            "   _Работает врачом._\n\n"
            "6️⃣ *Prepositional* — About/at. О ком?\n"
            "   _Думаю о студенте._"
        ),
        "zh": (
            "*俄语格系统*\n\n"
            "1️⃣ *主格* — 主语 Кто? Что?\n   _Студент читает._\n\n"
            "2️⃣ *属格* — 所属 Кого? Чего?\n   _Книга студента._\n\n"
            "3️⃣ *与格* — 给谁 Кому?\n   _Дать книгу студенту._\n\n"
            "4️⃣ *宾格* — 宾语 Кого? Что?\n   _Вижу студента._\n\n"
            "5️⃣ *工具格* — 用/作为 Кем?\n   _Работает врачом._\n\n"
            "6️⃣ *前置格* — 关于 О ком?\n   _Думаю о студенте._"
        ),
        "ar": (
            "*نظام الحالات الروسية*\n\n"
            "1️⃣ *الاسمية* — الفاعل\n   _Студент читает._\n\n"
            "2️⃣ *الملكية* — الملك\n   _Книга студента._\n\n"
            "3️⃣ *الإضافة* — لمن\n   _Дать книгу студенту._\n\n"
            "4️⃣ *المفعول به* — المفعول\n   _Вижу студента._\n\n"
            "5️⃣ *الأداة* — بواسطة\n   _Работает врачом._\n\n"
            "6️⃣ *الجر* — عن\n   _Думаю о студенте._"
        ),
        "es": (
            "*Casos del Ruso*\n\n"
            "1️⃣ *Nominativo* — Sujeto\n   _Студент читает._\n\n"
            "2️⃣ *Genitivo* — Posesión\n   _Книга студента._\n\n"
            "3️⃣ *Dativo* — A quién\n   _Дать книгу студенту._\n\n"
            "4️⃣ *Acusativo* — Objeto\n   _Вижу студента._\n\n"
            "5️⃣ *Instrumental* — Con/por\n   _Работает врачом._\n\n"
            "6️⃣ *Preposicional* — Sobre\n   _Думаю о студенте._"
        ),
    },
    "motion": {
        "title": "🚶 Глаголы движения",
        "en": (
            "*Verbs of Motion*\n\n"
            "Key rule: *unidirectional* vs *multidirectional*\n\n"
            "🚶 Walk: *идти* (now) / *ходить* (habit)\n"
            "🚗 Ride: *ехать* (now) / *ездить* (habit)\n"
            "✈️ Fly: *лететь* (now) / *летать* (habit)\n"
            "🏃 Run: *бежать* (now) / *бегать* (habit)\n\n"
            "📌 Examples:\n"
            "_Сейчас я иду в магазин._ (going now)\n"
            "_Я хожу в магазин каждый день._ (habit)\n"
            "_Завтра я еду в Москву._ (one trip)\n"
            "_Я часто езжу в Москву._ (repeatedly)"
        ),
        "zh": (
            "*运动动词*\n\n"
            "规则：*单向* vs *多向*\n\n"
            "🚶 步行: *идти*（现在）/ *ходить*（习惯）\n"
            "🚗 乘坐: *ехать*（现在）/ *ездить*（习惯）\n"
            "✈️ 飞行: *лететь*（现在）/ *летать*（习惯）\n\n"
            "📌 例句：\n"
            "_Сейчас я иду в магазин._ (正在去)\n"
            "_Я хожу в магазин каждый день._ (习惯)"
        ),
        "ar": (
            "*أفعال الحركة*\n\n"
            "القاعدة: *أحادي* vs *متعدد الاتجاهات*\n\n"
            "🚶 مشي: *идти* (الآن) / *ходить* (عادة)\n"
            "🚗 ركوب: *ехать* (الآن) / *ездить* (عادة)\n\n"
            "📌 أمثلة:\n"
            "_Сейчас я иду в магазин._ (أذهب الآن)\n"
            "_Я хожу в магазин каждый день._ (عادة)"
        ),
        "es": (
            "*Verbos de Movimiento*\n\n"
            "Regla: *unidireccional* vs *multidireccional*\n\n"
            "🚶 Caminar: *идти* (ahora) / *ходить* (hábito)\n"
            "🚗 Ir veh.: *ехать* (ahora) / *ездить* (hábito)\n\n"
            "📌 Ejemplos:\n"
            "_Сейчас я иду в магазин._ (voy ahora)\n"
            "_Я хожу в магазин каждый день._ (hábito)"
        ),
    },
}

VOCABULARY = {
    "en": (
        "📖 *Essential Russian Vocabulary*\n\n"
        "🏠 *Home:* дом, квартира, комната, кухня\n"
        "🍽️ *Food:* хлеб, вода, чай, кофе, суп\n"
        "🎓 *University:* студент, преподаватель, урок, экзамен\n"
        "🚌 *Transport:* автобус, метро, машина, поезд\n"
        "🔢 *Numbers 1-10:*\n"
        "один, два, три, четыре, пять,\n"
        "шесть, семь, восемь, девять, десять\n\n"
        "💡 Practice these in the Daily Quiz!"
    ),
    "zh": (
        "📖 *俄语基础词汇*\n\n"
        "🏠 *家庭:* дом(房子), квартира(公寓), комната(房间)\n"
        "🍽️ *食物:* хлеб(面包), вода(水), чай(茶), кофе(咖啡)\n"
        "🎓 *大学:* студент(学生), преподаватель(老师)\n"
        "🔢 *数字1-10:*\n один, два, три, четыре, пять,\n шесть, семь, восемь, девять, десять"
    ),
    "ar": (
        "📖 *مفردات روسية أساسية*\n\n"
        "🏠 *المنزل:* дом(بيت), квартира(شقة)\n"
        "🍽️ *الطعام:* хлеб(خبز), вода(ماء), чай(شاي)\n"
        "🎓 *الجامعة:* студент(طالب), преподаватель(أستاذ)\n"
        "🔢 *الأرقام 1-10:*\n один, два, три, четыре, пять,\n шесть, семь, восемь, девять, десять"
    ),
    "es": (
        "📖 *Vocabulario Esencial del Ruso*\n\n"
        "🏠 *Hogar:* дом(casa), квартира(apartamento)\n"
        "🍽️ *Comida:* хлеб(pan), вода(agua), чай(té)\n"
        "🎓 *Universidad:* студент(estudiante), преподаватель(profesor)\n"
        "🔢 *Números 1-10:*\n один, два, три, четыре, пять,\n шесть, семь, восемь, девять, десять"
    ),
}

def level_from_score(score, total):
    p = score / total
    if p < 0.4: return "A1"
    elif p < 0.6: return "A2"
    elif p < 0.8: return "B1"
    else: return "B2"

# ============================================================
# KEYBOARDS
# ============================================================

def kb_lang():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇬🇧 English", callback_data="setlang_en"),
            InlineKeyboardButton(text="🇨🇳 中文", callback_data="setlang_zh"),
        ],
        [
            InlineKeyboardButton(text="🇸🇦 العربية", callback_data="setlang_ar"),
            InlineKeyboardButton(text="🇪🇸 Español", callback_data="setlang_es"),
        ]
    ])

def kb_main(lang):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=tx(lang, "btn_quiz"))],
            [KeyboardButton(text=tx(lang, "btn_progress")),
             KeyboardButton(text=tx(lang, "btn_leaderboard"))],
            [KeyboardButton(text=tx(lang, "btn_grammar")),
             KeyboardButton(text=tx(lang, "btn_vocabulary"))],
            [KeyboardButton(text=tx(lang, "btn_settings"))],
        ],
        resize_keyboard=True
    )

def kb_placement_start():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Start Placement Test", callback_data="placement_start")]
    ])

def kb_options(opts):
    letters = ["A", "B", "C", "D"]
    rows = []
    for i, o in enumerate(opts):
        rows.append([InlineKeyboardButton(
            text=f"{letters[i]}. {o}",
            callback_data=f"qa_{i}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def kb_next(lang, is_last=False):
    label = tx(lang, "finish") if is_last else tx(lang, "next")
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=label, callback_data="qa_next")]
    ])

def kb_grammar(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Падежная система", callback_data="gr_cases")],
        [InlineKeyboardButton(text="🚶 Глаголы движения", callback_data="gr_motion")],
        [InlineKeyboardButton(text=tx(lang, "btn_back"), callback_data="go_menu")],
    ])

# ============================================================
# FSM STATES
# ============================================================

class Reg(StatesGroup):
    lang = State()
    placement = State()

class Quiz(StatesGroup):
    active = State()

# ============================================================
# ROUTER & HANDLERS
# ============================================================

router = Router()

# ---------- /start ----------
@router.message(CommandStart())
async def cmd_start(msg: Message, state: FSMContext):
    uid = msg.from_user.id
    user = await get_user(uid)

    if user and user["placement_done"]:
        lang = user["language"]
        await state.clear()
        await msg.answer(
            f"👋 {tx(lang,'menu')}",
            reply_markup=kb_main(lang)
        )
        return

    await create_user(uid, msg.from_user.username or "", msg.from_user.full_name or "")
    await state.set_state(Reg.lang)
    await msg.answer(
        "🇷🇺 *Welcome to RusBot!*\n\n"
        "Добро пожаловать | Welcome | 欢迎 | مرحباً | Bienvenido\n\n"
        "Choose your interface language / Выберите язык:",
        reply_markup=kb_lang(),
        parse_mode="Markdown"
    )

# ---------- Выбор языка (онбординг) ----------
@router.callback_query(Reg.lang, F.data.startswith("setlang_"))
async def cb_set_lang_reg(cb: CallbackQuery, state: FSMContext):
    lang = cb.data.split("_")[1]
    await update_user(cb.from_user.id, language=lang)
    await state.update_data(lang=lang, qi=0, score=0)
    await state.set_state(Reg.placement)
    await cb.message.edit_text(
        f"✅ Language set!\n\n📊 Now let's check your Russian level.\n"
        f"Take a short placement test (5 questions):",
        reply_markup=kb_placement_start()
    )
    await cb.answer()

# ---------- Старт теста ----------
@router.callback_query(Reg.placement, F.data == "placement_start")
async def cb_placement_start(cb: CallbackQuery, state: FSMContext):
    await send_placement_q(cb.message, state, edit=True)
    await cb.answer()

async def send_placement_q(msg, state, edit=False):
    data = await state.get_data()
    qi = data.get("qi", 0)
    lang = data.get("lang", "en")

    if qi >= len(PLACEMENT_TEST):
        await finish_placement(msg, state, lang)
        return

    q = PLACEMENT_TEST[qi]
    text = f"📝 *Question {qi+1}/{len(PLACEMENT_TEST)}*\n\n_{q['q']}_"
    kb = kb_options(q["opts"])

    if edit:
        await msg.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    else:
        await msg.answer(text, reply_markup=kb, parse_mode="Markdown")

# ---------- Ответ на placement ----------
@router.callback_query(Reg.placement, F.data.startswith("qa_"))
async def cb_placement_answer(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    qi = data.get("qi", 0)
    score = data.get("score", 0)
    lang = data.get("lang", "en")

    # игнорируем "qa_next" здесь — обрабатывается ниже
    if cb.data == "qa_next":
        await cb.answer()
        return

    if qi >= len(PLACEMENT_TEST):
        await cb.answer()
        return

    chosen = int(cb.data.split("_")[1])
    q = PLACEMENT_TEST[qi]
    correct = chosen == q["ans"]
    if correct:
        score += 1

    exp = q["exp"].get(lang, q["exp"]["en"])
    ans_text = q["opts"][q["ans"]]
    if correct:
        result = f"✅ *Correct!*\n\n💡 {exp}"
    else:
        result = f"❌ *Wrong!* Correct: *{ans_text}*\n\n💡 {exp}"

    new_qi = qi + 1
    is_last = new_qi >= len(PLACEMENT_TEST)
    await state.update_data(qi=new_qi, score=score)

    await cb.message.edit_text(
        result,
        reply_markup=kb_next(lang, is_last),
        parse_mode="Markdown"
    )
    await cb.answer()

# ---------- Следующий вопрос placement ----------
@router.callback_query(Reg.placement, F.data == "qa_next")
async def cb_placement_next(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    qi = data.get("qi", 0)
    lang = data.get("lang", "en")

    if qi >= len(PLACEMENT_TEST):
        await finish_placement(cb.message, state, lang, edit=True)
    else:
        await send_placement_q(cb.message, state, edit=True)
    await cb.answer()

async def finish_placement(msg, state, lang, edit=False):
    data = await state.get_data()
    score = data.get("score", 0)
    uid = msg.chat.id
    level = level_from_score(score, len(PLACEMENT_TEST))

    await update_user(uid, level=level, placement_done=1)
    await update_streak(uid)
    await state.clear()

    text = (
        f"🎉 *Placement Test Complete!*\n\n"
        f"📊 Score: {score}/{len(PLACEMENT_TEST)}\n"
        f"🏆 Your level: *{level}*\n\n"
        f"Welcome to RusBot! 🚀"
    )
    if edit:
        await msg.edit_text(text, parse_mode="Markdown")

    await msg.answer(
        tx(lang, "menu"),
        reply_markup=kb_main(lang)
    )

# ============================================================
# MAIN MENU HANDLERS
# ============================================================

async def get_lang(uid) -> str:
    u = await get_user(uid)
    return u["language"] if u else "en"

# ---------- Daily Quiz ----------
@router.message(F.text)
async def msg_handler(msg: Message, state: FSMContext):
    """Единый обработчик всех текстовых сообщений главного меню"""
    uid = msg.from_user.id
    user = await get_user(uid)
    if not user or not user["placement_done"]:
        return

    lang = user["language"]
    text = msg.text

    # --- Quiz ---
    if text == tx(lang, "btn_quiz"):
        await start_quiz(msg, state, user)

    # --- Progress ---
    elif text == tx(lang, "btn_progress"):
        await show_progress(msg, user)

    # --- Leaderboard ---
    elif text == tx(lang, "btn_leaderboard"):
        await show_leaderboard(msg, user)

    # --- Grammar ---
    elif text == tx(lang, "btn_grammar"):
        await msg.answer(
            "📚 *Grammar Topics / Темы грамматики*\nChoose a topic:",
            reply_markup=kb_grammar(lang),
            parse_mode="Markdown"
        )

    # --- Vocabulary ---
    elif text == tx(lang, "btn_vocabulary"):
        await msg.answer(
            VOCABULARY.get(lang, VOCABULARY["en"]),
            parse_mode="Markdown"
        )

    # --- Settings ---
    elif text == tx(lang, "btn_settings"):
        await msg.answer(
            "⚙️ *Settings*\nChange language / Сменить язык:",
            reply_markup=kb_lang(),
            parse_mode="Markdown"
        )

# ---------- QUIZ LOGIC ----------
async def start_quiz(msg: Message, state: FSMContext, user):
    lang = user["language"]
    level = user["level"]
    pool = DAILY_QUIZZES.get(level, DAILY_QUIZZES["A1"])
    questions = random.sample(pool, min(5, len(pool)))

    await state.set_state(Quiz.active)
    await state.update_data(
        questions=questions,
        qi=0,
        correct=0,
        lang=lang,
        level=level
    )
    await msg.answer(
        f"📝 *Daily Quiz — Level {level}*\n5 questions | Let's go! 🚀",
        parse_mode="Markdown"
    )
    await send_quiz_q(msg, questions[0], 0, len(questions), lang)

async def send_quiz_q(msg, q, qi, total, lang):
    text = f"❓ *Question {qi+1}/{total}*\n\n{q['q']}"
    await msg.answer(text, reply_markup=kb_options(q["opts"]), parse_mode="Markdown")

# ---------- Ответ Quiz ----------
@router.callback_query(Quiz.active, F.data.startswith("qa_"))
async def cb_quiz_answer(cb: CallbackQuery, state: FSMContext):
    if cb.data == "qa_next":
        await cb.answer()
        return

    data = await state.get_data()
    questions = data["questions"]
    qi = data["qi"]
    correct_count = data["correct"]
    lang = data["lang"]

    if qi >= len(questions):
        await cb.answer()
        return

    chosen = int(cb.data.split("_")[1])
    q = questions[qi]
    is_correct = chosen == q["ans"]
    xp = q.get("xp", 10) if is_correct else 0

    if is_correct:
        correct_count += 1
        result = tx(lang, "correct", xp=xp)
    else:
        result = tx(lang, "wrong", ans=q["opts"][q["ans"]])

    new_qi = qi + 1
    is_last = new_qi >= len(questions)
    await state.update_data(qi=new_qi, correct=correct_count)

    await cb.message.edit_text(
        result,
        reply_markup=kb_next(lang, is_last),
        parse_mode="Markdown"
    )
    await cb.answer()

# ---------- Следующий вопрос Quiz ----------
@router.callback_query(Quiz.active, F.data == "qa_next")
async def cb_quiz_next(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    questions = data["questions"]
    qi = data["qi"]
    correct_count = data["correct"]
    lang = data["lang"]
    level = data["level"]

    if qi >= len(questions):
        # Финиш
        total_xp = correct_count * 15
        await add_xp(cb.from_user.id, total_xp)
        await save_quiz_result(cb.from_user.id, level, correct_count, len(questions))
        await update_streak(cb.from_user.id)
        await state.clear()

        pct = int(correct_count / len(questions) * 100)
        emoji = "🏆" if pct == 100 else "👍" if pct >= 70 else "💪"

        text = (
            f"🎊 *Quiz Complete!*\n\n"
            f"✅ Correct: {correct_count}/{len(questions)}\n"
            f"📊 Accuracy: {pct}%\n"
            f"⭐ XP earned: +{total_xp}\n\n"
            f"{emoji} {'Perfect score!' if pct==100 else 'Great job!' if pct>=70 else 'Keep practicing!'}"
        )
        await cb.message.edit_text(text, parse_mode="Markdown")

        user = await get_user(cb.from_user.id)
        await cb.message.answer(
            tx(lang, "menu"),
            reply_markup=kb_main(lang)
        )
    else:
        q = questions[qi]
        await send_quiz_q(cb.message, q, qi, len(questions), lang)
        try:
            await cb.message.delete()
        except Exception:
            pass

    await cb.answer()

# ---------- Grammar callbacks ----------
@router.callback_query(F.data.startswith("gr_"))
async def cb_grammar(cb: CallbackQuery):
    lang = await get_lang(cb.from_user.id)
    topic = cb.data[3:]
    lesson = GRAMMAR_TOPICS.get(topic)
    if not lesson:
        await cb.answer("Not found")
        return

    content = lesson.get(lang, lesson.get("en", ""))
    await cb.message.edit_text(
        content,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=tx(lang, "btn_back"), callback_data="go_menu")]
        ])
    )
    await add_xp(cb.from_user.id, 5)
    await cb.answer("📚 +5 XP!")

# ---------- Back to menu ----------
@router.callback_query(F.data == "go_menu")
async def cb_go_menu(cb: CallbackQuery):
    lang = await get_lang(cb.from_user.id)
    try:
        await cb.message.delete()
    except Exception:
        pass
    await cb.message.answer(tx(lang, "menu"), reply_markup=kb_main(lang))
    await cb.answer()

# ---------- Settings: смена языка (вне онбординга) ----------
@router.callback_query(F.data.startswith("setlang_"))
async def cb_change_lang(cb: CallbackQuery, state: FSMContext):
    # Если идёт онбординг — не трогаем (обрабатывается выше через Reg.lang)
    current_state = await state.get_state()
    if current_state == Reg.lang.state:
        return

    lang = cb.data.split("_")[1]
    user = await get_user(cb.from_user.id)
    if not user or not user["placement_done"]:
        return

    await update_user(cb.from_user.id, language=lang)
    try:
        await cb.message.delete()
    except Exception:
        pass
    await cb.message.answer(
        f"✅ Language changed to {LANG_NAMES[lang]}",
        reply_markup=kb_main(lang)
    )
    await cb.answer()

# ---------- Progress ----------
async def show_progress(msg: Message, user):
    lang = user["language"]
    uid = user["user_id"]
    stats = await get_user_stats(uid)
    rank = await get_user_rank(uid)

    tq = stats["tq"] or 0
    tc = stats["tc"] or 0
    tt = stats["tt"] or 0
    acc = round(tc / tt * 100) if tt > 0 else 0

    xp = user["xp"]
    lvl = user["level"]
    thresholds = {"A1": (0, 200), "A2": (200, 500), "B1": (500, 1000), "B2": (1000, 1000)}
    lo, hi = thresholds.get(lvl, (0, 200))
    if hi > lo:
        filled = min(10, int((xp - lo) / (hi - lo) * 10))
        bar = "█" * filled + "░" * (10 - filled)
        bar_text = f"\n\n📊 XP Progress:\n[{bar}] {xp - lo}/{hi - lo}"
    else:
        bar_text = "\n\n🎓 Max level reached!"

    text = (
        f"📈 *My Progress*\n\n"
        f"👤 {user['full_name']}\n"
        f"📚 Level: *{lvl}*\n"
        f"⭐ XP: *{xp}*\n"
        f"🏅 Rank: *#{rank}*\n"
        f"🔥 Streak: *{user['streak']} days*\n\n"
        f"📝 Quizzes: *{tq}*\n"
        f"✅ Accuracy: *{acc}%*\n"
        f"💬 Total answers: *{tt}*"
        f"{bar_text}"
    )
    await msg.answer(text, parse_mode="Markdown")

# ---------- Leaderboard ----------
async def show_leaderboard(msg: Message, user):
    lang = user["language"]
    leaders = await get_leaderboard(10)
    my_rank = await get_user_rank(user["user_id"])
    medals = ["🥇", "🥈", "🥉"]

    text = "🏆 *Leaderboard — Top 10*\n\n"
    for i, l in enumerate(leaders):
        m = medals[i] if i < 3 else f"{i+1}."
        name = l["full_name"] or l["username"] or "Anonymous"
        me = " 👈 *You*" if l["user_id"] == user["user_id"] else ""
        text += f"{m} {name}{me}\n   ⭐ {l['xp']} XP | 📚 {l['level']} | 🔥 {l['streak']}d\n\n"

    if my_rank > 10:
        text += f"\n📍 Your position: #{my_rank}"

    await msg.answer(text, parse_mode="Markdown")

# ============================================================
# MAIN
# ============================================================

async def main():
    await init_db()
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    logging.info("🤖 RusBot started!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())