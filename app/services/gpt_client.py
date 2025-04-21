import base64, io, logging
from typing import Sequence, TypedDict
import openai, aiohttp
from app.config import settings

log = logging.getLogger(__name__)
openai.api_key = settings.OPENAI_API_KEY

class ImagePart(TypedDict):
    type: str
    image_url: dict[str, str]

async def _vision_from_bytes(img_bytes: bytes) -> ImagePart:
    b64 = base64.b64encode(img_bytes).decode()
    return {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}

async def ask_gpt(role_prompt: str, user_content: str,
                  images: list[bytes] | None = None,
                  tools: Sequence[dict] | None = None,
                  temperature: float = .7) -> str:
    """Универсальный вызов GPT‑4o (Vision или текст)."""
    messages: list[dict] = [{"role": "system", "content": role_prompt}]
    if images:
        img_parts = [await _vision_from_bytes(b) for b in images]
        messages.append({"role": "user", "content": img_parts + [{"type": "text", "text": user_content}]})
    else:
        messages.append({"role": "user", "content": user_content})

    resp = await openai.ChatCompletion.acreate(
        model=settings.GPT_MODEL,
        messages=messages,
        tools=tools,
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()
