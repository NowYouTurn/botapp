from aiogram import Router, F
from aiogram.types import Message
from io import BytesIO
from asyncio import create_task, sleep

from app.utils.typing_action import with_typing
from app.utils.credits import ensure_credit
from app.services.palmistry import analyze_palms
from app.models import User

router = Router()
_cache: dict[int, dict[str, bytes]] = {}


async def _purge(user_id: int, delay: int = 300):
    """Убрать фотографии из памяти через delay секунд."""
    await sleep(delay)
    _cache.pop(user_id, None)


@router.message(F.text == "✋ Хиромантия")
async def palm_intro(message: Message):
    await message.answer("Пришлите фото левой руки (укажите в подписи «левая»).")


@router.message(F.photo & (lambda m: m.caption and "лева" in m.caption.lower()))
async def palm_left(message: Message):
    # Сохраняем левую ладонь
    file = await message.bot.get_file(message.photo[-1].file_id)
    b = await message.bot.download_file(file.file_path)
    _cache[message.from_user.id] = {"left": b.read()}
    create_task(_purge(message.from_user.id))  # очистка через 5 минут
    await message.answer("Теперь пришлите фото правой руки (укажите «правая»).")


@router.message(F.photo & (lambda m: m.caption and "прав" in m.caption.lower()))
@with_typing
async def palm_right(message: Message, db_user: User):
    record = _cache.get(message.from_user.id)
    if not record or "left" not in record:
        await message.answer("Сначала отправьте левую руку.")
        return

    file = await message.bot.get_file(message.photo[-1].file_id)
    b = await message.bot.download_file(file.file_path)
    record["right"] = b.read()

    if not await ensure_credit(message, db_user):
        return

    result = await analyze_palms(record["left"], record["right"])
    await message.answer(result)
    _cache.pop(message.from_user.id, None)  # очистка сразу после анализа
