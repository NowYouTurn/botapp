import contextlib, asyncio, aiosqlite
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import event, text
from app.config import settings

# Включаем WAL для лучшей параллельной записи :contentReference[oaicite:6]{index=6}
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args={"timeout": 30},
)

@event.listens_for(engine.sync_engine, "connect")
def _set_sqlite_pragma(dbapi_conn, _):      # pragma: no cover
    if isinstance(dbapi_conn, aiosqlite.Connection):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

async_session_factory = async_sessionmaker(engine, expire_on_commit=False)

@contextlib.asynccontextmanager
async def get_session() -> AsyncSession:    # pragma: no cover
    async with async_session_factory() as sess:
        yield sess

async def init_db() -> None:
    """Создать таблицы (idempotent)."""
    from app import models  # noqa: F401 – декларирует Base.metadata
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
