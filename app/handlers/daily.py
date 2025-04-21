from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from app.utils.typing_action import with_typing
from apscheduler.triggers.cron import CronTrigger
from app.scheduler import scheduler
from app.utils.credits import ensure_credit
from app.models import User
import pendulum, re, logging

router = Router()
log = logging.getLogger(__name__)

@router.message(F.text == "🗓 Гороскоп на день")
async def choose_time(message: Message):
    await message.answer("Укажите время отправки (HH:MM) по вашему часовому поясу.")
    
@router.message(lambda m: re.fullmatch(r"\d{1,2}:\d{2}", m.text.strip()))
@with_typing
async def register_horo(message: Message, db_user: User):
    if not await ensure_credit(message, db_user): return
    hh, mm = map(int, message.text.split(":"))
    tz = db_user.timezone or "UTC"
    trigger = CronTrigger(hour=hh, minute=mm, timezone=tz)
    job_id = f"daily-{db_user.telegram_id}"
    scheduler.remove_job(job_id, silent=True)   # перезаписать, если был
    scheduler.add_job("app.scheduler:_send_daily", trigger, args=[message.bot, db_user],
                      id=job_id, replace_existing=True)
    await message.answer(f"✅ Ежедневный гороскоп будет приходить в {hh:02d}:{mm:02d} {tz}.",
                         reply_markup=ReplyKeyboardRemove())
