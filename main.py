import asyncio
import logging
import sys
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import config
from handlers import router
from ai_service import split_message
from database import get_daily_report_text

# Loglarni sozlash
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("BoshMuhandisBot")


async def set_bot_commands(bot: Bot):
    """Telegram menyusidagi standart buyruqlarni o'rnatish"""
    commands = [
        BotCommand(command="start", description="Bosh muhandis bilan muloqotni boshlash"),
        BotCommand(command="clear", description="Tarixni tozalash va yangi hisob-kitob"),
        BotCommand(command="report", description="Kunlik hisobotni ko'rish (Qabul qiluvchi uchun)"),
        BotCommand(command="admin", description="Admin boshqaruv paneli"),
        BotCommand(command="help", description="Ko'rsatmalar va me'yoriy ma'lumotlar"),
    ]
    await bot.set_my_commands(commands)


async def daily_report_scheduler(bot: Bot):
    """Har kuni belgilangan vaqtda (masalan, 21:00) hisobotni avtomatik yuborish"""
    last_sent_date = None
    logger.info(
        f"Kunlik hisobot xizmati faollashdi. Qabul qiluvchi ID: {config.REPORT_RECIPIENT_ID}, Vaqt: {config.DAILY_REPORT_TIME}"
    )

    while True:
        try:
            now = datetime.now()
            current_time_str = now.strftime("%H:%M")
            current_date_str = now.strftime("%Y-%m-%d")

            if current_time_str == config.DAILY_REPORT_TIME and last_sent_date != current_date_str:
                if config.REPORT_RECIPIENT_ID:
                    report_text = get_daily_report_text(current_date_str)
                    chunks = split_message(report_text, max_chars=4000)
                    for chunk in chunks:
                        try:
                            await bot.send_message(
                                chat_id=int(config.REPORT_RECIPIENT_ID),
                                text=chunk,
                                parse_mode=ParseMode.MARKDOWN,
                            )
                        except Exception as e:
                            logger.error(f"Hisobotni yuborishda xatolik: {e}")
                            try:
                                await bot.send_message(
                                    chat_id=int(config.REPORT_RECIPIENT_ID),
                                    text=chunk,
                                )
                            except Exception:
                                pass

                    last_sent_date = current_date_str
                    logger.info(
                        f"{current_date_str} kunlik hisoboti {config.REPORT_RECIPIENT_ID} ga muvaffaqiyatli yuborildi."
                    )
        except Exception as e:
            logger.error(f"Scheduler xatoligi: {e}")

        await asyncio.sleep(30)


async def main():
    logger.info("=== Bosh Muhandis va Smetachi Telegram Boti ishga tushirilmoqda ===")

    # Sozlamalarni tekshirish
    errors = config.validate_config()
    if errors:
        logger.warning("DIQQAT! Konfiguratsiyada kamchiliklar bor:")
        for err in errors:
            logger.warning(f" - {err}")
        logger.warning("Iltimos, .env faylini to'ldiring va botni qayta ishga tushiring.\n")

    if not config.BOT_TOKEN or config.BOT_TOKEN.startswith("your_"):
        logger.error(
            "XATOLIK: BOT_TOKEN ko'rsatilmagan! Bot ishga tusha olmaydi.\n"
            "Iltimos, @BotFather dan token olib, .env faylidagi BOT_TOKEN ga qo'ying."
        )
        return

    # Bot va Dispatcher yaratish
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )
    dp = Dispatcher()

    # Handlerlarni ulash
    dp.include_router(router)

    # Buyruqlar menyusini o'rnatish
    try:
        await set_bot_commands(bot)
        logger.info("Telegram buyruqlar menyusi o'rnatildi.")
    except Exception as e:
        logger.warning(f"Buyruqlar menyusini o'rnatishda xatolik: {e}")

    # Kunlik hisobot xizmatini fonda ishga tushirish
    asyncio.create_task(daily_report_scheduler(bot))

    # Pollingni boshlash
    logger.info("Bot tayyor va xabarlarni qabul qilmoqda...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logger.exception(f"Bot ishlashida xatolik yuz berdi: {e}")
    finally:
        await bot.session.close()
        logger.info("Bot sessiyasi yopildi.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
