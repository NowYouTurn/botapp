import pendulum
from app.services.gpt_client import ask_gpt

_SYSTEM_PROMPT = "Ты опытный астролог. Отвечай по‑русски."

async def yearly_forecast(natal_desc: str) -> str:
    return await ask_gpt(_SYSTEM_PROMPT,
        f"Составь подробный годовой прогноз (семья, отношения, деньги, карьера) "
        f"на основе натала:\n{natal_desc}")

async def daily_horoscope(natal_desc: str, for_date: pendulum.Date) -> str:
    return await ask_gpt(_SYSTEM_PROMPT,
        f"Составь краткий персональный гороскоп на {for_date.to_date_string()} "
        f"на основе этого описания натала:\n{natal_desc}",
        temperature=0.5)
