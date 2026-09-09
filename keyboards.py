from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Asosiy menyu tugmalari"""
    keyboard = [
        [
            KeyboardButton(text="🧱 Smeta hisoblash"),
            KeyboardButton(text="📐 TZ hisoblari"),
        ],
        [
            KeyboardButton(text="📋 Oferta (Tijorat taklifi)"),
            KeyboardButton(text="📑 Forma-2 va Forma-3"),
        ],
        [
            KeyboardButton(text="🧹 Yangi hisob-kitob"),
            KeyboardButton(text="ℹ️ Yo'riqnoma"),
        ],
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Vazifangiz yoki ob'ekt parametrlarini yozing...",
    )


def get_currency_inline_keyboard() -> InlineKeyboardMarkup:
    """Valyuta va hudud tanlash tugmalari"""
    buttons = [
        [
            InlineKeyboardButton(
                text="🇺🇿 O'zbekiston (So'm)", callback_data="curr_uzs"
            ),
            InlineKeyboardButton(
                text="🌐 Xalqaro (AQSH Dollari $)", callback_data="curr_usd"
            ),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
