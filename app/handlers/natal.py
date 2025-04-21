from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from app.keyboards import date_time as kb_dt, common as kb
from app.utils.typing_action import with_typing
from app.services.astrology import natal_chart_svg
from app.database import async_session_factory
from app.models import User
from pathlib import Path

router = Router()
_TMP: dict[int, dict] = {}

@router.message(F.text == "🌌 Натальная карта")
async def natal_entry(message: Message):
    await message.answer("Выбери год рождения:", reply_markup=kb_dt.year_keyboard())
    _TMP[message.chat.id] = {}

@router.callback_query(F.data.startswith("y:"))
async def choose_year(q: CallbackQuery):
    year = int(q.data.split(":")[1])
    _TMP[q.message.chat.id]["year"] = year
    await q.message.edit_text("Выбери месяц:", reply_markup=kb_dt.month_keyboard(year))

@router.callback_query(F.data.startswith("m:"))
async def choose_month(q: CallbackQuery):
    _, year, month = q.data.split(":")
    _TMP[q.message.chat.id]["month"] = int(month)
    await q.message.edit_text("Теперь день:", reply_markup=kb_dt.day_keyboard(int(year), int(month)))

@router.callback_query(F.data.startswith("d:"))
async def choose_day(q: CallbackQuery):
    _, y, m, d = q.data.split(":")
    _TMP[q.message.chat.id]["day"] = int(d)
    await q.message.edit_text("Укажи время (МСК):", reply_markup=kb_dt.time_keyboard(int(y), int(m), int(d)))

@router.callback_query(F.data.startswith("t:"))
@with_typing
async def final_time(q: CallbackQuery, db_user: User):
    _, y, m, d, h, mn = q.data.split(":")
    data = _TMP.pop(q.message.chat.id)
    date_str = f"{y}-{int(m):02d}-{int(d):02d}"
    time_str = f"{int(h):02d}:{int(mn):02d}"
    await q.message.answer("Напиши город рождения:")
    data.update({"date": date_str, "time": time_str})
    _TMP[q.message.chat.id] = data  # сохранить до ввода города

@router.message(lambda m: m.chat.id in _TMP and "city" not in _TMP[m.chat.id])
@with_typing
async def city_input(message: Message, db_user: User):
    data = _TMP.pop(message.chat.id)
    city = message.text.strip()
    data["city"] = city
    svg_path: Path = await natal_chart_svg(
        message.from_user.first_name, data["date"], data["time"], data["city"]
    )
    await message.answer_document(svg_path.open("rb"), caption="Твоя натальная карта 🌌")
    # сохранить в БД
    async with async_session_factory() as s:
        db_user.free_used = True
        await s.commit()
