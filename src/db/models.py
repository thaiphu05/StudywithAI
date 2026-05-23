from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class AccountDB(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        CheckConstraint("role IN ('admin', 'user')", name="ck_accounts_role"),
    )

    account_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(10), nullable=False, default="user")
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    account_type: Mapped[str] = mapped_column(String(10), nullable=False, default="normal")
    token_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=10000)
    token_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    plan_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    tokens_reset_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
