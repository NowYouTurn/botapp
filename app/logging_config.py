import logging, asyncio, datetime as dt
from logging.handlers import TimedRotatingFileHandler, QueueHandler, QueueListener
from asyncio import Queue
from app.database import async_session_factory
from app.models import Log
from app.config import settings

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

class AsyncDBHandler(logging.Handler):
    """Неблокирующее сохранение логов в таблицу logs."""

    def __init__(self, level=logging.INFO):
        super().__init__(level)
        self.queue: Queue[logging.LogRecord] = Queue()
        self.listener = QueueListener(
            self.queue, self._handle, respect_handler_level=True
        )
        self.listener.start()

    async def _write(self, record: logging.LogRecord):
        async with async_session_factory() as s:
            s.add(Log(level=record.levelname, msg=self.format(record)))
            await s.commit()

    def _handle(self, record: logging.LogRecord):
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(self._write(record))
        else:
            asyncio.run(self._write(record))

    def emit(self, record: logging.LogRecord):
        self.queue.put_nowait(record)

def setup_logging() -> None:
    root = logging.getLogger()
    root.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    root.handlers.clear()

    file_handler = TimedRotatingFileHandler(
        "logs/bot.log", when="midnight", backupCount=7, encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(_LOG_FORMAT))

    db_handler = AsyncDBHandler()
    db_handler.setFormatter(logging.Formatter(_LOG_FORMAT))

    root.addHandler(file_handler)
    root.addHandler(db_handler)
