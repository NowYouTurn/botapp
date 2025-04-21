from uuid import uuid4
from aiogram.types import Message
from app.config import settings
from app.database import async_session_factory
from app.models import User

def make_ref_link(bot_name: str, user: User) -> str:
    return f"https://t.me/{bot_name}?start={user.id}_{uuid4().hex[:6]}"

async def register_user(message: Message, ref_param: str | None) -> User:
    async with async_session_factory() as s:
        user = await s.scalar(
            User.__table__.select().where(User.telegram_id == message.from_user.id)
        )
        if not user:
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                referrer_id=int(ref_param.split("_")[0]) if ref_param else None,
            )
            s.add(user)
            await s.commit()
        return user
