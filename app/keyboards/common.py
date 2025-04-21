from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from app.models import PayPack

# --- Reply‑меню ----
MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🌌 Натальная карта"), KeyboardButton(text="🔮 Прогноз на год")],
        [KeyboardButton(text="❤️ Совместимость"), KeyboardButton(text="🗓 Гороскоп на день")],
        [KeyboardButton(text="🌙 Сонник"), KeyboardButton(text="✨ Приметы")],
        [KeyboardButton(text="✋ Хиромантия"), KeyboardButton(text="💳 Пополнить услуги")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие",
)

def payment_keyboard() -> InlineKeyboardMarkup:
    rows = []
    for pack in PayPack:
        rows.append([
            InlineKeyboardButton(
                text=f"{pack.qty} усл. — {pack.price} ₽", callback_data=f"buy:{pack.name}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def confirm_spend() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Списать 1 услугу", callback_data="spend:yes")],
            [InlineKeyboardButton(text="Отмена", callback_data="spend:no")],
        ]
    )
