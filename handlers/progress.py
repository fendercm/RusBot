from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

import database as db
from content import t, LEVEL_PROGRESSION
from keyboards import main_menu_keyboard, back_to_menu_keyboard

router = Router()


@router.message(F.text)
async def show_progress(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user:
        return

    lang = user["language"]
    if message.text != t(lang, "my_progress"):
        return

    stats = await db.get_user_stats(message.from_user.id)
    rank = await db.get_user_rank(message.from_user.id)

    total_quizzes = stats["total_quizzes"] or 0
    total_correct = stats["total_correct"] or 0
    total_questions = stats["total_questions"] or 0

    accuracy = (
        round(total_correct / total_questions * 100)
        if total_questions > 0 else 0
    )

    next_level = LEVEL_PROGRESSION.get(user["level"], user["level"])

    # XP прогресс-бар
    xp = user["xp"]
    xp_levels = {"A1": 0, "A2": 200, "B1": 500, "B2": 1000}
    current_xp_threshold = xp_levels.get(user["level"], 0)
    next_xp_threshold = xp_levels.get(next_level, current_xp_threshold + 500)

    if next_level != user["level"]:
        progress = min(xp - current_xp_threshold, next_xp_threshold - current_xp_threshold)
        needed = next_xp_threshold - current_xp_threshold
        bar_filled = int((progress / needed) * 10) if needed > 0 else 10
        bar = "█" * bar_filled + "░" * (10 - bar_filled)
        progress_text = f"\n\n📊 Progress to {next_level}:\n[{bar}] {progress}/{needed} XP"
    else:
        progress_text = "\n\n🎓 Maximum level reached!"

    text = (
        f"📈 *My Progress*\n\n"
        f"👤 {user['full_name']}\n"
        f"🏆 {t(lang, 'level_label')}: **{user['level']}**\n"
        f"⭐ {t(lang, 'xp_label')}: **{user['xp']}**\n"
        f"🏅 {t(lang, 'rank_label')}: **#{rank}**\n"
        f"🔥 {t(lang, 'streak_label')}: **{user['streak']} {t(lang, 'days_label')}**\n"
        f"\n📝 Quizzes completed: **{total_quizzes}**\n"
        f"✅ Accuracy: **{accuracy}%**\n"
        f"💬 Total answers: **{total_questions}**"
        f"{progress_text}"
    )

    await message.answer(text, parse_mode="Markdown")