from aiogram import Router, F
from aiogram.types import Message
from app.utils.typing_action import with_typing
from app.utils.credits import ensure_credit
from app.services.gpt_client import ask_gpt
from app.models import User

router = Router()
_PROMPT = ("На основе двух натальных карт оцени совместимость в процентах, "
           "а затем дай подробный анализ по домам (отношения, финансы, карьера).")

@router.message(F.text == "❤️ Совместимость")
async def ask_data(message: Message):
    await message.answer("Введите данные двух людей: "
                         "`Имя1 YYYY‑MM‑DD HH:MM Город1; "
                         "Имя2 YYYY‑MM‑DD HH:MM Город2`")

@router.message(lambda m: ";" in m.text and m.text.count(" ") >= 7)
@with_typing
async def compat_calc(message: Message, db_user: User):
    if not await ensure_credit(message, db_user): return
    text = message.text
    result = await ask_gpt("Ты астролог‑совместимость", f"{_PROMPT}\n{text}")
    await message.answer(result)
