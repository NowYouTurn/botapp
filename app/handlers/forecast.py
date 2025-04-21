from aiogram import Router, F
from aiogram.types import Message
from app.services.horoscope import yearly_forecast
from app.utils.typing_action import with_typing
from app.utils.credits import ensure_credit
from app.models import User

router = Router()

@router.message(F.text == "🔮 Прогноз на год")
@with_typing
async def yearly(message: Message, db_user: User):
    if not await ensure_credit(message, db_user): return
    natal_desc = "…"  # можно вытянуть из сохранённого SVG‑описания
    text = await yearly_forecast(natal_desc)
    await message.answer(text)
