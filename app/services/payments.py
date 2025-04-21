# app/services/payments.py
from uuid import uuid4
from typing import Any

from yookassa import Configuration, Payment as YoPayment
from yookassa.domain.models.currency import Currency  # ✔ актуальный путь в SDK 3
from app.config import settings
from app.database import async_session_factory
from app.models import Payment, PayPack, PayStatus

Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


async def create_payment(user_id: int, pack: PayPack) -> Any:
    """
    Создает платеж и сохраняет запись в базе.
    Возвращает объект ответа YooKassa (у него есть .confirmation.confirmation_url).
    """
    order_id = str(uuid4())
    payment = YoPayment.create(
        {
            "amount": {"value": f"{pack.price:.2f}", "currency": Currency.RUB},
            "confirmation": {"type": "redirect", "return_url": settings.WEBHOOK_URL},
            "capture": True,
            "description": f"Покупка {pack.qty} услуг",
            "metadata": {"order_id": order_id, "user_id": user_id},
        }
    )

    async with async_session_factory() as session:
        session.add(
            Payment(
                order_id=order_id,
                payment_id=payment.id,
                qty=pack.qty,
                amount=pack.price,
                user_id=user_id,
            )
        )
        await session.commit()

    return payment  # у call‑site берём .confirmation.confirmation_url


async def mark_paid(payment_id: str):
    """Пометить платеж как оплаченный и обновить статус."""
    async with async_session_factory() as session:
        await session.execute(
            Payment.__table__.update()
            .where(Payment.payment_id == payment_id)
            .values(status=PayStatus.paid)
        )
        await session.commit()
