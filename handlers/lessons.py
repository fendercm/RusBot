from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

import database as db
from content import t, GRAMMAR_LESSONS
from keyboards import (
    main_menu_keyboard, grammar_topics_keyboard, back_to_menu_keyboard
)

router = Router()


@router.message(F.text)
async def show_grammar_menu(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user:
        return
    lang = user["language"]
    if message.text != t(lang, "grammar"):
        return

    await message.answer(
        "📚 *Grammar Topics*\n\nChoose a topic to study:",
        reply_markup=grammar_topics_keyboard(lang),
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("grammar_"))
async def show_grammar_lesson(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    lang = user["language"] if user else "en"

    topic = callback.data.replace("grammar_", "")
    lesson = GRAMMAR_LESSONS.get(topic)

    if not lesson:
        await callback.answer("Lesson not found")
        return

    content = lesson["content"].get(lang, lesson["content"]["en"])

    await callback.message.edit_text(
        f"*{lesson['title']}*\n{content}",
        reply_markup=back_to_menu_keyboard(lang),
        parse_mode="Markdown"
    )

    # Дать XP за изучение урока
    await db.add_xp(callback.from_user.id, 5)
    await callback.answer("📚 +5 XP for studying!")


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    lang = user["language"] if user else "en"

    await callback.message.delete()
    await callback.message.answer(
        t(lang, "main_menu"),
        reply_markup=main_menu_keyboard(lang)
    )
    await callback.answer()


@router.message(F.text)
async def handle_vocabulary(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user:
        return
    lang = user["language"]
    if message.text != t(lang, "vocabulary"):
        return

    vocab_text = (
        "📖 *Russian Vocabulary — Essential Words*\n\n"
        "🏠 *Home*\n"
        "дом — house | квартира — apartment\n"
        "комната — room | кухня — kitchen\n\n"
        "🍽️ *Food*\n"
        "хлеб — bread | вода — water\n"
        "чай — tea | кофе — coffee\n\n"
        "🎓 *University*\n"
        "студент — student | преподаватель — teacher\n"
        "урок — lesson | экзамен — exam\n\n"
        "🔢 *Numbers 1-10*\n"
        "один, два, три, четыре, пять\n"
        "шесть, семь, восемь, девять, десять\n\n"
        "💡 Practice these words in the daily quiz!"
    )

    await message.answer(vocab_text, parse_mode="Markdown")


@router.message(F.text)
async def handle_settings(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user:
        return
    lang = user["language"]
    if message.text != t(lang, "settings"):
        return

    from keyboards import language_keyboard
    await message.answer(
        "⚙️ *Settings*\n\nChange interface language:",
        reply_markup=language_keyboard(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("lang_"))
async def change_language_settings(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    if not user or user["placement_done"] == 0:
        return

    lang = callback.data.split("_")[1]
    await db.update_user(callback.from_user.id, language=lang)

    await callback.message.edit_text(f"✅ {t(lang, 'language_set')}")
    await callback.message.answer(
        t(lang, "main_menu"),
        reply_markup=main_menu_keyboard(lang)
    )
    await callback.answer()