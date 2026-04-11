from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class AccountDB(Base):
    __tablename__ = "accounts"

    account_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    token_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=200000)
    token_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
