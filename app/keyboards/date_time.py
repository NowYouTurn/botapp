from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import calendar, datetime as dt

def year_keyboard(start: int = 1940, end: int | None = None) -> InlineKeyboardMarkup:
    end = end or dt.date.today().year
    inline = [[
        InlineKeyboardButton(str(y), callback_data=f"y:{y}")
        for y in range(row, row + 4)
    ] for row in range(start, end + 1, 4)]
    return InlineKeyboardMarkup(inline_keyboard=inline)

def month_keyboard(year: int) -> InlineKeyboardMarkup:
    months = ["Янв","Фев","Мар","Апр","Май","Июн","Июл","Авг","Сен","Окт","Ноя","Дек"]
    inline = [[
        InlineKeyboardButton(months[i], callback_data=f"m:{year}:{i+1}")
        for i in range(r, r+3)
    ] for r in range(0, 12, 3)]
    return InlineKeyboardMarkup(inline_keyboard=inline)

def day_keyboard(year: int, month: int) -> InlineKeyboardMarkup:
    month_range = calendar.monthrange(year, month)[1]
    inline = []
    row = []
    for d in range(1, month_range+1):
        row.append(InlineKeyboardButton(str(d), callback_data=f"d:{year}:{month}:{d}"))
        if len(row) == 7:
            inline.append(row); row = []
    if row: inline.append(row)
    return InlineKeyboardMarkup(inline_keyboard=inline)

def time_keyboard(year: int, month: int, day: int) -> InlineKeyboardMarkup:
    def _buttons(step: int):
        return [
            InlineKeyboardButton(f"{h:02d}:{m:02d}",
                                 callback_data=f"t:{year}:{month}:{day}:{h}:{m}")
            for h in range(0, 24, 3) for m in (0, step)
        ]
    inline = []
    btns = _buttons(0)
    for i in range(0, len(btns), 6):
        inline.append(btns[i:i+6])
    return InlineKeyboardMarkup(inline_keyboard=inline)
