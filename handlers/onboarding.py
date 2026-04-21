from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from content import t, PLACEMENT_TEST, determine_level_from_score
from keyboards import (
    language_keyboard, main_menu_keyboard,
    quiz_options_keyboard, next_question_keyboard, placement_start_keyboard
)

router = Router()


class OnboardingStates(StatesGroup):
    choosing_language = State()
    placement_test = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = await db.get_user(user_id)

    if user and user["placement_done"]:
        lang = user["language"]
        await message.answer(
            f"👋 {t(lang, 'main_menu')}!",
            reply_markup=main_menu_keyboard(lang)
        )
        return

    await db.create_user(
        user_id,
        message.from_user.username or "",
        message.from_user.full_name or ""
    )

    await state.set_state(OnboardingStates.choosing_language)
    await message.answer(
        TRANSLATIONS_WELCOME,
        reply_markup=language_keyboard()
    )


TRANSLATIONS_WELCOME = (
    "🇷🇺 *Welcome to RusBot!*\n\n"
    "Добро пожаловать | Welcome | 欢迎 | مرحباً | Bienvenido\n\n"
    "Please choose your interface language:\n"
    "Пожалуйста, выберите язык интерфейса:"
)


@router.callback_query(F.data.startswith("lang_"))
async def choose_language(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    user_id = callback.from_user.id

    await db.update_user(user_id, language=lang)
    await callback.message.edit_text(
        f"{t(lang, 'language_set')}\n\n{t(lang, 'choose_level')}",
        reply_markup=placement_start_keyboard(lang)
    )
    await state.set_state(OnboardingStates.placement_test)
    await state.update_data(lang=lang, q_index=0, score=0)
    await callback.answer()


@router.callback_query(F.data == "start_placement")
async def start_placement(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "en")
    await send_placement_question(callback.message, state, lang, 0, edit=True)
    await callback.answer()


async def send_placement_question(message, state, lang, index, edit=False):
    if index >= len(PLACEMENT_TEST):
        await finish_placement(message, state, lang)
        return

    q = PLACEMENT_TEST[index]
    text = (
        f"📝 *Question {index + 1}/{len(PLACEMENT_TEST)}*\n\n"
        f"_{q['question']}_"
    )
    kb = quiz_options_keyboard(q["options"], lang)

    if edit:
        await message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    else:
        await message.answer(text, reply_markup=kb, parse_mode="Markdown")


@router.callback_query(
    OnboardingStates.placement_test,
    F.data.startswith("answer_")
)
async def handle_placement_answer(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "en")
    q_index = data.get("q_index", 0)
    score = data.get("score", 0)

    if q_index >= len(PLACEMENT_TEST):
        await callback.answer()
        return

    q = PLACEMENT_TEST[q_index]
    chosen = int(callback.data.split("_")[1])
    is_correct = chosen == q["correct"]

    if is_correct:
        score += 1

    explanation = q["explanation"].get(lang, q["explanation"]["en"])
    correct_option = q["options"][q["correct"]]

    if is_correct:
        result_text = f"✅ *Correct!*\n\n💡 {explanation}"
    else:
        result_text = f"❌ *Wrong!* Correct: *{correct_option}*\n\n💡 {explanation}"

    next_index = q_index + 1
    is_last = next_index >= len(PLACEMENT_TEST)

    await state.update_data(q_index=next_index, score=score)

    await callback.message.edit_text(
        result_text,
        reply_markup=next_question_keyboard(lang, is_last),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(OnboardingStates.placement_test, F.data == "next_question")
async def placement_next(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "en")
    q_index = data.get("q_index", 0)
    score = data.get("score", 0)

    if q_index >= len(PLACEMENT_TEST):
        await finish_placement(callback.message, state, lang, score=score, edit=True)
    else:
        await send_placement_question(callback.message, state, lang, q_index, edit=True)
    await callback.answer()


async def finish_placement(message, state, lang, score=None, edit=False):
    data = await state.get_data()
    if score is None:
        score = data.get("score", 0)
    user_id = message.chat.id

    level = determine_level_from_score(score, len(PLACEMENT_TEST))
    await db.update_user(user_id, level=level, placement_done=1)
    await db.update_streak(user_id)

    text = (
        f"🎉 *Placement Test Complete!*\n\n"
        f"📊 Score: {score}/{len(PLACEMENT_TEST)}\n"
        f"🏆 Your level: *{level}*\n\n"
        f"Welcome to RusBot! Your learning journey begins! 🚀"
    )

    await state.clear()

    if edit:
        await message.edit_text(text, parse_mode="Markdown")
        await message.answer(
            t(lang, "main_menu"),
            reply_markup=main_menu_keyboard(lang)
        )
    else:
        await message.answer(text, parse_mode="Markdown")
        await message.answer(
            t(lang, "main_menu"),
            reply_markup=main_menu_keyboard(lang)
        )