from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from app.keyboards.common import payment_keyboard
from app.services.payments import create_payment
from app.models import PayPack, User
import logging

router = Router()
log = logging.getLogger(__name__)

@router.message(F.text == "💳 Пополнить услуги")
async def show_packs(message: Message):
    await message.answer("Выберите пакет:", reply_markup=payment_keyboard())

@router.callback_query(F.data.startswith("buy:"))
async def buy_pack(cb: CallbackQuery, db_user: User):
    pack_name = cb.data.split(":")[1]
    pack = PayPack[pack_name]
    payment = await create_payment(db_user.id, pack)
    await cb.message.edit_text(
    f"Оплатите {pack.price} ₽ по ссылке:\n{payment.confirmation.confirmation_url}\n"
    "После успешной оплаты услуги будут начислены автоматически. Спасибо!"
)
