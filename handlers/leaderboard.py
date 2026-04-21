from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

import database as db
from content import t
from keyboards import main_menu_keyboard, back_to_menu_keyboard

router = Router()

MEDALS = ["🥇", "🥈", "🥉"]


@router.message(F.text)
async def show_leaderboard(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user:
        return

    lang = user["language"]
    if message.text != t(lang, "leaderboard"):
        return

    leaders = await db.get_leaderboard(10)
    my_rank = await db.get_user_rank(message.from_user.id)

    text = "🏆 *Leaderboard — Top 10*\n\n"

    for i, leader in enumerate(leaders):
        medal = MEDALS[i] if i < 3 else f"{i + 1}."
        name = leader["full_name"] or leader["username"] or "Anonymous"
        is_me = leader["user_id"] == message.from_user.id
        marker = " 👈 *You*" if is_me else ""

        text += (
            f"{medal} {name}{marker}\n"
            f"   ⭐ {leader['xp']} XP | "
            f"📚 {leader['level']} | "
            f"🔥 {leader['streak']} days\n\n"
        )

    if my_rank > 10:
        text += f"\n📍 Your position: #{my_rank}"

    await message.answer(text, parse_mode="Markdown")