import logging, asyncio, time
from aiogram.types import Message, CallbackQuery
from app.keyboards.common import confirm_spend
from app.database import async_session_factory
from app.models import User

log = logging.getLogger(__name__)

# очистка просроченных запросов подтверждения
_pending: dict[int, float] = {}
_TIMEOUT = 300  # 5 минут


async def ensure_credit(event: Message | CallbackQuery, user: User) -> bool:
    """
    Проверить баланс, запросить подтверждение расхода 1 услуги,
    списать её в БД или вернуть False, если оплату не удалось подтвердить.
    """
    chat_id = event.chat.id if isinstance(event, Message) else event.message.chat.id

    # первая бесплатная
    if not user.free_used:
        async with async_session_factory() as s:
            user.free_used = True
            await s.commit()
        return True

    # баланс
    if user.credits <= 0:
        await event.answer("❌ У вас нет оплаченных услуг. Пополните счёт 💳")
        return False

    # уже спрашивали – ждём ответа в callback
    if chat_id in _pending and time.time() - _pending[chat_id] < _TIMEOUT:
        await event.answer("Подтвердите списание через появившиеся кнопки 🖱")
        return False

    msg = await event.answer(
        f"⚠️ Списать 1 услугу? У вас останется {user.credits - 1}.",
        reply_markup=confirm_spend(),
    )
    _pending[chat_id] = time.time()

    try:
        cb: CallbackQuery = await event.bot.wait_for(
            CallbackQuery,
            timeout=_TIMEOUT,
            check=lambda c: c.message.id == msg.message_id and c.data.startswith("spend:"),
        )
    except asyncio.TimeoutError:
        await msg.edit_text("⏱ Время подтверждения истекло.")
        _pending.pop(chat_id, None)
        return False

    _pending.pop(chat_id, None)
    if cb.data.endswith("yes"):
        async with async_session_factory() as s:
            user.credits -= 1
            await s.commit()
        await cb.message.edit_text("✅ Услуга списана.")
        return True

    await cb.message.edit_text("Операция отменена.")
    return False
