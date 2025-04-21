import logging, pendulum, asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.database import async_session_factory
from app.models import User
from app.services.horoscope import daily_horoscope
from aiogram import Bot

log = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

async def _send_daily(bot: Bot, user: User):
    natal_desc = "..."  # here could be cached/interpolated description
    today = pendulum.now(user.timezone or "UTC").date()
    text = await daily_horoscope(natal_desc, today)
    await bot.send_message(user.telegram_id, text)

async def schedule_jobs(bot: Bot):
    async with async_session_factory() as s:
        users = (await s.execute(User.__table__.select())).fetchall()
    for row in users:
        user: User = row[0]
        if user.timezone:
            scheduler.add_job(
                _send_daily, CronTrigger(hour=9, minute=0, timezone=user.timezone),
                args=[bot, user], id=f"daily-{user.telegram_id}", replace_existing=True
            )
    scheduler.start()
