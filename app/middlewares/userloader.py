from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Awaitable, Dict, Any
from sqlalchemy import select

from app.database import async_session_factory
from app.models import User


class UserMiddleware(BaseMiddleware):
    """
    Подгружает объект User из БД и кладёт в data["db_user"].
    Если пользователя нет — создаётся запись‑заглушка (id появится позже в обработчике /start).
    """

    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ):
        tg_id = event.from_user.id
        async with async_session_factory() as session:
            user = await session.scalar(select(User).where(User.telegram_id == tg_id))
            if not user:                                # создать временного гостя
                user = User(telegram_id=tg_id, username=event.from_user.username)
                session.add(user)
                await session.commit()
            data["db_user"] = user
        return await handler(event, data)
