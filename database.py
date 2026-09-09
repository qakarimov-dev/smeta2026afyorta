import sqlite3
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Any

DB_PATH = Path(__file__).resolve().parent / "smeta.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    """Ma'lumotlar bazasini ishga tushirish"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS calculations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                full_name TEXT,
                prompt TEXT NOT NULL,
                response TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def save_calculation(user_id: int, username: str, full_name: str, prompt: str, response: str):
    """Foydalanuvchi bajargan har bir hisob-kitobni saqlash"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO calculations (user_id, username, full_name, prompt, response, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                username or "",
                full_name or "",
                prompt,
                response,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        conn.commit()


def get_daily_calculations(target_date: str = None) -> List[Dict[str, Any]]:
    """Muayyan kunda bajarilgan barcha hisob-kitoblarni olish"""
    if target_date is None:
        target_date = date.today().strftime("%Y-%m-%d")

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, user_id, username, full_name, prompt, response, created_at
            FROM calculations
            WHERE created_at LIKE ?
            ORDER BY created_at ASC
            """,
            (f"{target_date}%",),
        )
        rows = cursor.fetchall()

    results = []
    for row in rows:
        results.append(
            {
                "id": row[0],
                "user_id": row[1],
                "username": row[2],
                "full_name": row[3],
                "prompt": row[4],
                "response": row[5],
                "created_at": row[6],
            }
        )
    return results


def get_daily_report_text(target_date: str = None) -> str:
    """Kunlik hisobot matnini shakllantirish"""
    if target_date is None:
        target_date = date.today().strftime("%Y-%m-%d")

    records = get_daily_calculations(target_date)
    if not records:
        return f"📊 **Kunlik Qurilish Hisoboti ({target_date})**\n\nBugun hech qanday hisob-kitob amalga oshirilmadi."

    unique_users = set(r["user_id"] for r in records)

    report_lines = [
        f"📊 **KUNLIK QURILISH VA SMETA HISOBOTI**",
        f"📅 **Sana:** `{target_date}`",
        f"👥 **Faol foydalanuvchilar soni:** {len(unique_users)} ta",
        f"📝 **Jami hisob-kitoblar soni:** {len(records)} ta\n",
        f"────────────────────────",
    ]

    for idx, item in enumerate(records, 1):
        uname = f"@{item['username']}" if item["username"] else item["full_name"] or str(item["user_id"])
        short_prompt = item["prompt"]
        if len(short_prompt) > 120:
            short_prompt = short_prompt[:120] + "..."

        # Javobdan qisqa xulosa yoki asosiy raqamlar
        short_response = item["response"]
        if len(short_response) > 180:
            short_response = short_response[:180] + "..."

        time_str = item["created_at"].split(" ")[-1] if " " in item["created_at"] else item["created_at"]

        report_lines.append(
            f"**#{idx} | Vaqt: {time_str}**\n"
            f"👤 **Foydalanuvchi:** {uname} (`ID: {item['user_id']}`)\n"
            f"📌 **So'rov:** _{short_prompt}_\n"
            f"📄 **Hisob natijasi (qisqacha):**\n{short_response}\n"
            f"────────────────────────"
        )

    return "\n".join(report_lines)


def get_total_statistics() -> Dict[str, Any]:
    """Barcha vaqtlar va bugungi umumiy statistika"""
    today_str = date.today().strftime("%Y-%m-%d")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*), COUNT(DISTINCT user_id) FROM calculations")
        row1 = cursor.fetchone()
        total_calc, total_users = row1 if row1 else (0, 0)

        cursor.execute(
            "SELECT COUNT(*), COUNT(DISTINCT user_id) FROM calculations WHERE created_at LIKE ?",
            (f"{today_str}%",),
        )
        row2 = cursor.fetchone()
        today_calc, today_users = row2 if row2 else (0, 0)

    return {
        "total_calc": total_calc or 0,
        "total_users": total_users or 0,
        "today_calc": today_calc or 0,
        "today_users": today_users or 0,
    }


# Modul yuklanganda jadvalni yaratish
init_db()
