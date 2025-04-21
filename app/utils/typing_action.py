"""Декоратор для длительных задач: показывает 'typing…' пока выполняется корутина."""
import asyncio, functools, logging
from typing import Callable, Any
from aiogram.types import Message
from aiogram import Bot

logger = logging.getLogger(__name__)

def with_typing(func: Callable) -> Callable:
    @functools.wraps(func)
    async def wrapper(message: Message, *args, **kwargs) -> Any:
        bot: Bot = message.bot
        async def _ticker():
            try:
                while True:
                    await bot.send_chat_action(message.chat.id, "typing")
                    await asyncio.sleep(4)  # индикатор действует ≤5 с :contentReference[oaicite:6]{index=6}
            except asyncio.CancelledError:
                pass

        task = asyncio.create_task(_ticker())
        try:
            return await func(message, *args, **kwargs)
        finally:
            task.cancel()

    return wrapper
