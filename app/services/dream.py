from app.services.gpt_client import ask_gpt

_PROMPT = ("Ты сонник‑аналитик. У тебя есть четыре сонника: Миллера, Цветкова, Фрейда и Ванги. "
           "Дай трактовку сна с учётом дня недели, сначала сведи в единую оценку, затем пиши разбор "
           "от каждого сонника отдельным абзацем.")

async def interpret_dream(text: str, weekday: str) -> str:
    return await ask_gpt(_PROMPT,
        f"Пользователь видел сон в ночь на {weekday}. Сон описан так:\n{text}\n\nДай толкование.")
