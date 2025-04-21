from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from app.utils.typing_action import with_typing
from app.utils.credits import ensure_credit
from app.services.dream import interpret_dream
from app.models import User

router = Router()

WEEKDAYS = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

# Клавиатура выбора дня недели
weekday_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=d, callback_data=f"dream_w:{idx}")]
        for idx, d in enumerate(WEEKDAYS)
    ]
)

# временный кэш <user_id -> weekday>
_pending_weekday: dict[int, str] = {}


@router.message(F.text == "🌙 Сонник")
async def dream_entry(message: Message):
    await message.answer("Выберите день недели, когда приснился сон:", reply_markup=weekday_kb)


@router.callback_query(F.data.startswith("dream_w:"))
async def dream_chosen_weekday(cb):
    idx = int(cb.data.split(":")[1])
    _pending_weekday[cb.from_user.id] = WEEKDAYS[idx]
    await cb.message.edit_text("Теперь опишите сон одним сообщением.")


@router.message(lambda m: m.from_user.id in _pending_weekday)
@with_typing
async def dream_interpret(message: Message, db_user: User):
    weekday = _pending_weekday.pop(message.from_user.id)
    if not await ensure_credit(message, db_user):
        return
    answer = await interpret_dream(message.text, weekday)
    await message.answer(answer)
