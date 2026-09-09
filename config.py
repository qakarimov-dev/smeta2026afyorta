import os
from pathlib import Path
from dotenv import load_dotenv

# .env faylini yuklash
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

# Telegram sozlamalari
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Adminlar ro'yxati
ADMIN_IDS_RAW = os.getenv("ADMIN_IDS", os.getenv("ADMIN_ID", "")).strip()
ADMIN_IDS = [
    int(x.strip()) for x in ADMIN_IDS_RAW.split(",") if x.strip().isdigit()
]

# Kunlik hisobot qabul qiluvchi
REPORT_RECIPIENT_ID = os.getenv("REPORT_RECIPIENT_ID", "5532937776").strip()
DAILY_REPORT_TIME = os.getenv("DAILY_REPORT_TIME", "21:00").strip()


def is_admin(user_id: int | str) -> bool:
    """Foydalanuvchi admin ekanligini tekshirish"""
    try:
        return int(user_id) in ADMIN_IDS
    except (ValueError, TypeError):
        return False


def can_view_reports(user_id: int | str) -> bool:
    """Hisobotni ko'rish huquqi (Adminlar yoki belgilangan hisobot egasi)"""
    if is_admin(user_id):
        return True
    try:
        return str(user_id) == str(REPORT_RECIPIENT_ID)
    except Exception:
        return False

# AI provayderi ('gemini' yoki 'openai')
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").strip().lower()

# API kalitlari
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

# Model nomlari
AI_MODEL = os.getenv("AI_MODEL", "").strip()
if not AI_MODEL:
    if AI_PROVIDER == "openai":
        AI_MODEL = "gpt-4o-mini"
    else:
        AI_MODEL = "gemini-2.5-flash"

# Kontekst tarixi chuqurligi
try:
    MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "10"))
except ValueError:
    MAX_HISTORY_MESSAGES = 10


def validate_config() -> list[str]:
    """Konfiguratsiya to'liqligini tekshirish"""
    errors = []
    if not BOT_TOKEN or BOT_TOKEN.startswith("your_"):
        errors.append("BOT_TOKEN belgilanmagan yoki noto'g'ri. .env faylida @BotFather bergan tokenni kiriting.")

    if AI_PROVIDER == "gemini":
        if not GEMINI_API_KEY or GEMINI_API_KEY.startswith("AIzaSy..."):
            errors.append("GEMINI_API_KEY belgilanmagan. https://aistudio.google.com/ dan kalit oling.")
    elif AI_PROVIDER == "openai":
        if not OPENAI_API_KEY or OPENAI_API_KEY.startswith("sk-..."):
            errors.append("OPENAI_API_KEY belgilanmagan. https://platform.openai.com/ dan kalit oling.")
    else:
        errors.append(f"Noma'lum AI_PROVIDER: '{AI_PROVIDER}'. Faqat 'gemini' yoki 'openai' bo'lishi kerak.")

    return errors
