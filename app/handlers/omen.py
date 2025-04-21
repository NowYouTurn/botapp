from aiogram import Router, F
from aiogram.types import Message
from app.utils.typing_action import with_typing
from app.utils.credits import ensure_credit
from app.services.omen import explain_omen
from app.models import User

router = Router()


@router.message(F.text == "✨ Приметы")
async def omen_entry(message: Message):
    await message.answer("Введите примету, которую хотите объяснить.")


@router.message(lambda m: m.reply_to_message and "примету" in (m.reply_to_message.text or ""))
@with_typing
async def omen_answer(message: Message, db_user: User):
    if not await ensure_credit(message, db_user):
        return
    result = await explain_omen(message.text)
    await message.answer(result)
