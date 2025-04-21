# app/bot.py
import logging
import asyncio
import json
import hmac
import hashlib
from pathlib import Path
from fastapi import FastAPI, Request, Response, BackgroundTasks
from fastapi.responses import JSONResponse
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.webhook.aiohttp_server import setup_application
from app.config import settings
from app.logging_config import setup_logging
from app.handlers import routers as h_routers
from app.middlewares.userloader import UserMiddleware
from app.database import init_db, async_session_factory
from app.models import Payment, PayStatus, PayPack, User
from app.scheduler import scheduler, schedule_jobs
from yookassa import Webhook
from yookassa.domain.notification import WebhookNotificationEventType
from app.services.payments import mark_paid

# Инициализация логирования
setup_logging()
log = logging.getLogger(__name__)

# Исправленная инициализация бота
bot = Bot(
    settings.TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()
dp.update.middleware(UserMiddleware())

# Включаем все роутеры
for router in h_routers:
    dp.include_router(router)

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await init_db()
    
    # Устанавливаем вебхук через метод бота
    await bot.set_webhook(
        url=settings.WEBHOOK_URL,
        drop_pending_updates=True
    )
    
    await schedule_jobs(bot)
    log.info("Application started")

@app.post("/webhook")
async def telegram_webhook(request: Request) -> Response:
    # Исправленный обработчик обновлений
    update = await request.json()
    await dp.feed_webhook_update(bot, update)
    return JSONResponse({"ok": True})

@app.post("/yookassa")
async def yoo_hook(request: Request, bg: BackgroundTasks):
    # Проверка подписи
    raw = await request.body()
    sig = request.headers.get("Content-HMAC-SHA256", "")
    
    # Генерация HMAC
    secret = settings.YOOKASSA_SECRET_KEY.encode()
    digest = hmac.new(secret, raw, hashlib.sha256).hexdigest()
    
    if not hmac.compare_digest(digest, sig):
        log.warning("Invalid HMAC signature")
        return Response(status_code=401)

    # Обработка платежа
    payload = json.loads(raw)
    if payload["event"] != WebhookNotificationEventType.PAYMENT_SUCCEEDED:
        return Response(status_code=200)
    
    payment_id = payload["object"]["id"]
    bg.add_task(process_payment_task, payment_id)
    return Response(status_code=200)

async def process_payment_task(payment_id: str):
    try:
        await mark_paid(payment_id)
        async with async_session_factory() as session:
            # Получаем данные платежа
            payment = await session.scalar(
                select(Payment).where(Payment.payment_id == payment_id)
            )
            
            if not payment or payment.status != PayStatus.paid:
                return

            # Обновляем баланс пользователя
            user = await session.scalar(
                select(User).where(User.id == payment.user_id)
            )
            user.credits += payment.qty
            await session.commit()
            
            # Отправляем уведомление
            await bot.send_message(
                chat_id=user.telegram_id,
                text=f"🎉 Спасибо за покупку! Начислено {payment.qty} услуг. Текущий баланс: {user.credits}."
            )
    except Exception as e:
        log.error(f"Payment processing error: {str(e)}")

def main():
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_config=None,  # Используем нашу конфигурацию логирования
    )

if __name__ == "__main__":
    main()