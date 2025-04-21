import io, logging
from app.services.gpt_client import ask_gpt

log = logging.getLogger(__name__)

_PROMPT = ("Ты профессиональный хиромант. Проанализируй основные линии: судьбы, жизни, головы, сердца, "
           "Меркурия, солнца. Дай выводы и рекомендации простым языком.")

async def analyze_palms(left_bytes: bytes, right_bytes: bytes) -> str:
    return await ask_gpt(_PROMPT, "Анализируй ладони пользователя.",
                         images=[left_bytes, right_bytes], temperature=0.4)
