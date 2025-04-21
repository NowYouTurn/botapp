from aiogram import Router, F
from aiogram.types import Message
from app.config import settings
from app.models import User
from app.keyboards.common import MAIN_MENU
from app.services.referral import register_user
from app.utils.typing_action import with_typing

router = Router()

@router.message(F.text == "/start")
@with_typing
async def cmd_start(message: Message):
    param = message.get_args()
    user = await register_user(message, param or None)
    name = message.from_user.username or message.from_user.first_name
    await message.answer(
        f"Привет, {name}! Я астробот. Выбери интересующую функцию 👇",
        reply_markup=MAIN_MENU
    )
