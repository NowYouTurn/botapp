from functools import lru_cache
from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    # --- TG & OpenAI ---
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    GPT_MODEL: str = os.getenv("GPT_MODEL", "gpt-4o-mini-2024-07-18")
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL")

    # --- YooKassa ---
    YOOKASSA_SHOP_ID: str = os.getenv("YOOKASSA_SHOP_ID")
    YOOKASSA_SECRET_KEY: str = os.getenv("YOOKASSA_SECRET_KEY")

    # --- DB ---
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/bot.db")

    # --- Admins & Legal ---
    ADMIN_IDS: set[int] = {
        int(i) for i in os.getenv("ADMIN_IDS", "").split(",") if i.strip()
    }
    POLICY_URL: str = os.getenv("POLICY_URL")
    OFFER_URL: str = os.getenv("OFFER_URL")

    # Runtime
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

@lru_cache(1)
def get_settings() -> Settings:   # pragma: no cover
    return Settings()

settings = get_settings()
