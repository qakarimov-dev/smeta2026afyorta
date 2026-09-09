import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.enums import ChatAction

import config
from prompts import START_MESSAGE, HELP_MESSAGE
from keyboards import get_main_keyboard, get_currency_inline_keyboard
from ai_service import ai_service, conversation_manager, split_message
from database import save_calculation, get_daily_report_text, get_total_statistics

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def handle_start(message: Message):
    """Start buyrug'i"""
    conversation_manager.clear(message.chat.id)
    await message.answer(
        START_MESSAGE,
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown",
    )


@router.message(Command("help"))
@router.message(F.text == "ℹ️ Yo'riqnoma")
async def handle_help(message: Message):
    """Yordam va ko'rsatmalar"""
    await message.answer(
        HELP_MESSAGE,
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown",
    )


@router.message(Command("clear"))
@router.message(F.text == "🧹 Yangi hisob-kitob")
async def handle_clear(message: Message):
    """Hisob-kitob tarixini tozalash"""
    conversation_manager.clear(message.chat.id)
    await message.answer(
        "🔄 **Bosh muhandis xotirasi tozalandi.**\n\n"
        "Yangi ob'ekt yoki loyiha parametrlarini kiriting. "
        "Smeta, Oferta yoki Texnik topshiriq (TZ) tuzishga tayyorman.",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown",
    )


@router.message(Command("admin"))
async def handle_admin_command(message: Message):
    """Adminlar uchun boshqaruv paneli"""
    if not config.is_admin(message.from_user.id):
        await message.answer("⚠️ Bu buyruq faqat bot adminlari uchun mo'ljallangan.")
        return

    stats = get_total_statistics()
    admin_list = ", ".join(f"`{aid}`" for aid in config.ADMIN_IDS) if config.ADMIN_IDS else "Mavjud emas"

    admin_text = (
        "👑 **Bosh Muhandis Bot — Admin Paneli**\n\n"
        "📊 **Umumiy statistika:**\n"
        f"• Jami foydalanuvchilar: **{stats['total_users']}** ta\n"
        f"• Jami hisob-kitoblar: **{stats['total_calc']}** ta\n"
        f"• Bugungi faol foydalanuvchilar: **{stats['today_users']}** ta\n"
        f"• Bugungi yangi hisob-kitoblar: **{stats['today_calc']}** ta\n\n"
        "⚙️ **Tizim sozlamalari:**\n"
        f"• AI modeli: `{config.AI_PROVIDER}` (`{config.AI_MODEL}`)\n"
        f"• Kunlik hisobot oluvchi: `{config.REPORT_RECIPIENT_ID}`\n"
        f"• Hisobot vaqti: `{config.DAILY_REPORT_TIME}`\n"
        f"• Tayinlangan adminlar: {admin_list}\n\n"
        "📌 **Mavjud buyruqlar:**\n"
        "• `/report` — Bugungi kunlik barcha hisob-kitoblar hisoboti\n"
        "• `/clear` — Xotirani tozalash"
    )
    await message.answer(admin_text, parse_mode="Markdown")


@router.message(Command("report"))
@router.message(Command("hisobot"))
async def handle_report_command(message: Message):
    """Qabul qiluvchi yoki Admin uchun kunlik hisobotni talab bo'yicha ko'rsatish"""
    if not config.can_view_reports(message.from_user.id):
        await message.answer("⚠️ Bu buyruq faqat hisobot qabul qiluvchi yoki adminlar uchun mo'ljallangan.")
        return

    report_text = get_daily_report_text()
    chunks = split_message(report_text, max_chars=4000)
    for chunk in chunks:
        try:
            await message.answer(chunk, parse_mode="Markdown")
        except Exception:
            await message.answer(chunk)


@router.message(F.text == "🧱 Smeta hisoblash")
async def handle_smeta_button(message: Message):
    """Smeta hisoblash bo'yicha tezkor ko'rsatma"""
    await message.answer(
        "🧱 **Smeta hisoblash bo'limi:**\n\n"
        "Iltimos, ob'ekt hajmini va ish turini yozing. Masalan:\n"
        "• *«150 kv.m polda 5 sm qalinlikda sementli styajka quyish smetasi»*\n"
        "• *«120 kv.m xonadonni to'liq ta'mirlash smetasi»*\n\n"
        "Valyutani oldindan tanlashingiz ham mumkin:",
        reply_markup=get_currency_inline_keyboard(),
        parse_mode="Markdown",
    )


@router.message(F.text == "📐 TZ hisoblari")
async def handle_tz_button(message: Message):
    """Texnik topshiriq va material/resurs hisoblari"""
    await message.answer(
        "📐 **Texnik topshiriq (TZ) va resurslar hisobi:**\n\n"
        "Qurilish hajmidan kelib chiqib quyidagilarni aniqlab beraman:\n"
        "1. ShNQ bo'yicha materiallar sarfi va isrof (otxod) ko'rsatkichi.\n"
        "2. Ishchi kuchi me'yoriy sarfi (odam-soat).\n"
        "3. Mashina va mexanizmlar zaruriyati (mashina-soat).\n"
        "4. Texnologik ketma-ketlik va xavfsizlik choralari.\n\n"
        "Hisoblamoqchi bo'lgan qurilish hajmini yozing:",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown",
    )


@router.message(F.text == "📋 Oferta (Tijorat taklifi)")
async def handle_oferta_button(message: Message):
    """Oferta tayyorlash bo'limi"""
    await message.answer(
        "📋 **Oferta (Tijorat taklifi) tuzish:**\n\n"
        "Pudratchi yoki buyurtmachi uchun yuridik va texnik jihatdan to'liq taklif tayyorlayman.\n"
        "Quyidagi ma'lumotlarni yozing:\n"
        "• Ob'ekt va bajariladigan ishlar nomi;\n"
        "• Mo'ljallangan umumiy byudjet yoki hajm;\n"
        "• Rejalashtirilgan muddat (kun/oy).\n\n"
        "Men to'lov bosqichlari, kafolatlar va javobgarlik chegaralarini qonuniy me'yorlar asosida rasmiylashtirib beraman.",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown",
    )


@router.message(F.text == "📑 Forma-2 va Forma-3")
async def handle_forms_button(message: Message):
    """Qurilish formalarini shakllantirish"""
    await message.answer(
        "📑 **Qurilish hujjatlari va davlat standart formalari:**\n\n"
        "Quyidagi rasmiy hujjatlarni tayyorlab beraman:\n"
        "• **Forma-2:** Bajarilgan ishlar dalolatnomasi (KC-2);\n"
        "• **Forma-3:** Sarf-xarajat ma'lumotnomasi (KC-3);\n"
        "• **Defekt dalolatnomasi:** Nuqsonlar va zaruriy ishlar bayoni;\n"
        "• **M-29 shakli:** Materiallarni hisobdan chiqarish hisoboti.\n\n"
        "Qaysi ob'ekt yoki ishlar bo'yicha hujjat kerakligini yozing:",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown",
    )


@router.callback_query(F.data.startswith("curr_"))
async def handle_currency_callback(callback: CallbackQuery):
    """Valyuta tanlash callback handleri"""
    currency_code = callback.data.replace("curr_", "")
    if currency_code == "uzs":
        text = "O'zbekiston sharoitida (O'zbekiston so'mida)"
        prompt_inject = "Eslatma: Foydalanuvchi hisob-kitobni O'zbekiston so'mida (UZS) bajarishni tanladi."
    else:
        text = "Xalqaro sharoitda (AQSH dollarida $)"
        prompt_inject = "Eslatma: Foydalanuvchi hisob-kitobni AQSH dollarida (USD $) bajarishni tanladi."

    conversation_manager.add_message(callback.message.chat.id, "user", prompt_inject)
    conversation_manager.add_message(
        callback.message.chat.id,
        "model",
        f"Tushunarli, barcha narx hisob-kitoblari {text} amalga oshiriladi. Ob'ekt hajmini va parametrlarini yozing.",
    )

    await callback.answer(f"Tanlandi: {text}")
    await callback.message.answer(
        f"✅ Hisob-kitob valyutasi: **{text}** qilib belgilandi.\n\n"
        f"Endi ob'ekt hajmi va parametrlarini yozing:",
        parse_mode="Markdown",
    )


@router.message(F.text)
async def handle_user_query(message: Message):
    """Foydalanuvchining barcha muhandislik savollari va smeta so'rovlari"""
    user_text = message.text.strip()
    chat_id = message.chat.id

    # Telegramda "yozmoqda..." holatini ko'rsatish
    await message.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    # AI javobini olish
    reply_text = await ai_service.get_response(chat_id=chat_id, user_message=user_text)

    # Hisob-kitobni bazaga saqlash (kunlik hisobot uchun)
    try:
        save_calculation(
            user_id=message.from_user.id,
            username=message.from_user.username or "",
            full_name=message.from_user.full_name or "",
            prompt=user_text,
            response=reply_text,
        )
    except Exception as e:
        logger.error(f"Hisob-kitobni bazaga saqlashda xatolik: {e}")

    # Telegram chekloviga ko'ra matnni bo'lish
    chunks = split_message(reply_text, max_chars=4000)

    for chunk in chunks:
        try:
            # Avval chiroyli Markdown formatida yuborishga urinish
            await message.answer(chunk, parse_mode="Markdown")
        except Exception as e:
            logger.warning(f"Markdown parse xatoligi ({e}), oddiy matn sifatida yuborilmoqda.")
            # Agar Markdown sintaksisida maxsus belgilar xato keltirsa, oddiy matn qilib yuborish
            await message.answer(chunk)
