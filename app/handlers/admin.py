from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select
import re, logging

from app.filters.is_admin import IsAdmin
from app.database import async_session_factory
from app.models import User

router = Router()
log = logging.getLogger(__name__)


@router.message(IsAdmin(), F.text.startswith("/give"))
async def give_credits(message: Message):
    """
    /give <tg_id|@username> <кол-во>
    """
    mt = re.match(r"/give\s+(\S+)\s+(\d+)", message.text)
    if not mt:
        await message.answer("Формат: /give <tg_id|@username> <кол-во>")
        return

    ident, qty = mt.groups()
    qty = int(qty)

    async with async_session_factory() as s:
        if ident.startswith("@"):
            user = await s.scalar(select(User).where(User.username == ident.lstrip("@")))
        else:
            user = await s.scalar(select(User).where(User.telegram_id == int(ident)))

        if not user:
            await message.answer("❌ Пользователь не найден.")
            return

        user.credits += qty
        await s.commit()

    await message.answer(f"✅ Начислил {qty} услуг пользователю {user.telegram_id}.")


@router.message(IsAdmin(), F.text == "/stats")
async def stats(message: Message):
    async with async_session_factory() as s:
        total = await s.scalar(select(User).count())
    await message.answer(f"👥 Всего пользователей: {total}")
