import aiosqlite
import asyncio
from datetime import datetime, date

DB_PATH = "rusbot.db"


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
                last_activity DATE,
                placement_done INTEGER DEFAULT 0,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                topic TEXT,
                correct INTEGER,
                total INTEGER,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS daily_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                activity_date DATE,
                lessons_done INTEGER DEFAULT 0,
                xp_earned INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        await db.commit()


async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ) as cursor:
            return await cursor.fetchone()


async def create_user(user_id: int, username: str, full_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO users (user_id, username, full_name)
            VALUES (?, ?, ?)
        """, (user_id, username, full_name))
        await db.commit()


async def update_user(user_id: int, **kwargs):
    if not kwargs:
        return
    fields = ", ".join(f"{k} = ?" for k in kwargs)
    values = list(kwargs.values()) + [user_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            f"UPDATE users SET {fields} WHERE user_id = ?", values
        )
        await db.commit()


async def add_xp(user_id: int, amount: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET xp = xp + ? WHERE user_id = ?",
            (amount, user_id)
        )
        await db.commit()


async def update_streak(user_id: int):
    """Обновляет стрик пользователя"""
    user = await get_user(user_id)
    today = date.today()

    if user is None:
        return

    last = user["last_activity"]

    async with aiosqlite.connect(DB_PATH) as db:
        if last is None:
            await db.execute(
                "UPDATE users SET streak = 1, last_activity = ? WHERE user_id = ?",
                (today, user_id)
            )
        else:
            last_date = date.fromisoformat(str(last))
            diff = (today - last_date).days
            if diff == 1:
                await db.execute(
                    "UPDATE users SET streak = streak + 1, last_activity = ? WHERE user_id = ?",
                    (today, user_id)
                )
            elif diff > 1:
                await db.execute(
                    "UPDATE users SET streak = 1, last_activity = ? WHERE user_id = ?",
                    (today, user_id)
                )
        await db.commit()


async def save_quiz_result(user_id: int, topic: str, correct: int, total: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO quiz_results (user_id, topic, correct, total)
            VALUES (?, ?, ?, ?)
        """, (user_id, topic, correct, total))
        await db.commit()


async def get_leaderboard(limit: int = 10):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT user_id, full_name, username, xp, level, streak
            FROM users
            ORDER BY xp DESC
            LIMIT ?
        """, (limit,)) as cursor:
            return await cursor.fetchall()


async def get_user_stats(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT 
                COUNT(*) as total_quizzes,
                SUM(correct) as total_correct,
                SUM(total) as total_questions,
                MAX(completed_at) as last_quiz
            FROM quiz_results
            WHERE user_id = ?
        """, (user_id,)) as cursor:
            return await cursor.fetchone()


async def get_user_rank(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT COUNT(*) + 1 as rank FROM users
            WHERE xp > (SELECT xp FROM users WHERE user_id = ?)
        """, (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0