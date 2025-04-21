import datetime as dt
import uuid
from enum import Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float, DateTime, Text, ForeignKey, Enum as SAEnum

class Base(DeclarativeBase):
    pass

# --- Users -------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(32))
    email: Mapped[str | None] = mapped_column(String(128))
    timezone: Mapped[str | None] = mapped_column(String(64))
    free_used: Mapped[bool] = mapped_column(default=False)
    credits: Mapped[int] = mapped_column(Integer, default=0)
    referrer_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"))
    referred: Mapped[list["User"]] = relationship(
        "User", backref="referrer", remote_side=[id]
    )
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)

# --- Payments ---------------------------------------------
class PayPack(Enum):
    one = (1, 99)
    three = (3, 279)
    five = (5, 449)
    ten = (10, 849)
    twenty = (20, 1499)

    @property
    def qty(self): return self.value[0]     # type: ignore
    @property
    def price(self): return self.value[1]   # type: ignore

class PayStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    cancelled = "cancelled"

class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[str] = mapped_column(String(64), default=lambda: str(uuid.uuid4()))
    payment_id: Mapped[str | None] = mapped_column(String(64))
    qty: Mapped[int] = mapped_column(Integer)
    amount: Mapped[float] = mapped_column(Float)
    status: Mapped[PayStatus] = mapped_column(SAEnum(PayStatus), default=PayStatus.pending)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)

# --- Logs --------------------------------------------------
class Log(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    level: Mapped[str] = mapped_column(String(20))
    msg: Mapped[str] = mapped_column(Text)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
