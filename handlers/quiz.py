from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import random

import database as db
from content import t, DAILY_QUIZZES
from keyboards import quiz_options_keyboard, next_question_keyboard, main_menu_keyboard

router = Router()


class QuizStates(StatesGroup):
    in_quiz = State()


@router.message(F.text.contains("Quiz") | F.text.contains("测验") | F.text.contains("اختبار") | F.text.contains("Quiz"))
async def start_daily_quiz(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    if not user:
        await message.answer("Please use /start first")
        return

    lang = user["language"]
    level = user["level"]

    # Проверяем текст кнопки
    btn_text = t(lang, "start_quiz")
    if message.text != btn_text:
        return

    questions = DAILY_QUIZZES.get(level, DAILY_QUIZZES["A1"])
    quiz_questions = random.sample(questions, min(5, len(questions)))

    await state.set_state(QuizStates.in_quiz)
    await state.update_data(
        questions=quiz_questions,
        q_index=0,
        correct=0,
        lang=lang,
        level=level
    )

    await message.answer(
        f"📝 *Daily Quiz — Level {level}*\n"
        f"5 questions | Let's go! 🚀",
        parse_mode="Markdown"
    )
    await send_quiz_question(message, state, quiz_questions[0], 0, len(quiz_questions))


async def send_quiz_question(message, state, question: dict, index: int, total: int):
    data = await state.get_data()
    lang = data.get("lang", "en")

    text = (
        f"❓ *Question {index + 1}/{total}*\n\n"
        f"{question['question']}"
    )
    await message.answer(
        text,
        reply_markup=quiz_options_keyboard(question["options"], lang),
        parse_mode="Markdown"
    )


@router.callback_query(QuizStates.in_quiz, F.data.startswith("answer_"))
async def handle_quiz_answer(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "en")
    questions = data.get("questions", [])
    q_index = data.get("q_index", 0)
    correct_count = data.get("correct", 0)

    if q_index >= len(questions):
        await callback.answer()
        return

    q = questions[q_index]
    chosen = int(callback.data.split("_")[1])
    is_correct = chosen == q["correct"]
    xp_gained = q.get("xp", 10) if is_correct else 0

    if is_correct:
        correct_count += 1
        result = f"✅ {t(lang, 'correct', xp=xp_gained)}"
    else:
        correct_answer = q["options"][q["correct"]]
        result = f"❌ {t(lang, 'wrong', answer=correct_answer)}"

    next_index = q_index + 1
    is_last = next_index >= len(questions)

    await state.update_data(q_index=next_index, correct=correct_count)

    await callback.message.edit_text(
        result,
        reply_markup=next_question_keyboard(lang, is_last),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(QuizStates.in_quiz, F.data == "next_question")
async def quiz_next_question(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "en")
    questions = data.get("questions", [])
    q_index = data.get("q_index", 0)
    correct_count = data.get("correct", 0)
    level = data.get("level", "A1")

    if q_index >= len(questions):
        # Финиш квиза
        total_xp = sum(
            q.get("xp", 10) for i, q in enumerate(questions) if i < correct_count
        )
        # Примерный XP
        total_xp = correct_count * 15

        await db.add_xp(callback.from_user.id, total_xp)
        await db.save_quiz_result(
            callback.from_user.id, level, correct_count, len(questions)
        )
        await db.update_streak(callback.from_user.id)

        result_text = (
            f"🎊 *Quiz Complete!*\n\n"
            f"{t(lang, 'quiz_result', correct=correct_count, total=len(questions), xp=total_xp)}\n\n"
        )

        if correct_count == len(questions):
            result_text += "🏆 Perfect score! Excellent! 🌟"
        elif correct_count >= len(questions) * 0.7:
            result_text += "👍 Great job! Keep it up!"
        else:
            result_text += "💪 Keep practicing! You'll get better!"

        await state.clear()
        await callback.message.edit_text(result_text, parse_mode="Markdown")

        user = await db.get_user(callback.from_user.id)
        await callback.message.answer(
            t(lang, "main_menu"),
            reply_markup=main_menu_keyboard(lang)
        )
    else:
        await send_quiz_question(
            callback.message, state, questions[q_index], q_index, len(questions)
        )
        try:
            await callback.message.delete()
        except:
            pass

    await callback.answer()