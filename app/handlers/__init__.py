# app/handlers/__init__.py
"""
Агрегирует все Router‑объекты, чтобы бот мог одним импортом подключить их.
Добавляйте новый роутер ниже, и он автоматически появится в приложении.
"""

from .start import router as start_router
from .natal import router as natal_router
from .forecast import router as forecast_router
from .compat import router as compat_router
from .daily import router as daily_router
from .dream import router as dream_router
from .omen import router as omen_router
from .palm import router as palm_router
from .payments import router as payments_router
from .admin import router as admin_router

# Глобальный список
routers = [
    start_router,
    natal_router,
    forecast_router,
    compat_router,
    daily_router,
    dream_router,
    omen_router,
    palm_router,
    payments_router,
    admin_router,
]

__all__ = ["routers"]  # чтобы из пакета экспортировался только этот объект
