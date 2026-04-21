from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from content import t

def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton(text="🇨🇳 中文", callback_data="lang_zh"),
        ],
        [
            InlineKeyboardButton(text="🇸🇦 العربية", callback_data="lang_ar"),
            InlineKeyboardButton(text="🇪🇸 Español", callback_data="lang_es"),
        ]
    ])

def main_menu_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "start_quiz"))],
            [KeyboardButton(text=t(lang, "my_progress")), KeyboardButton(text=t(lang, "leaderboard"))],
            [KeyboardButton(text=t(lang, "grammar")), KeyboardButton(text=t(lang, "vocabulary"))],
            [KeyboardButton(text=t(lang, "settings"))],
        ],
        resize_keyboard=True
    )

def quiz_options_keyboard(options: list, lang: str, is_last: bool = False) -> InlineKeyboardMarkup:
    buttons = []
    for i, option in enumerate(options):
        buttons.append([InlineKeyboardButton(
            text=f"{['A', 'B', 'C', 'D'][i]}. {option}",
            callback_data=f"answer_{i}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def next_question_keyboard(lang: str, is_last: bool = False) -> InlineKeyboardMarkup:
    text = t(lang, "finish") if is_last else t(lang, "next")
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, callback_data="next_question")]
    ])

def back_to_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "back"), callback_data="back_to_menu")]
    ])

def grammar_topics_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Падежная система", callback_data="grammar_cases")],
        [InlineKeyboardButton(text="🚶 Глаголы движения", callback_data="grammar_verbs_of_motion")],
        [InlineKeyboardButton(text=t(lang, "back"), callback_data="back_to_menu")],
    ])

def placement_start_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Start Test", callback_data="start_placement")]
    ])