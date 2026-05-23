from collections.abc import Callable
from datetime import datetime, timezone
from typing import Literal

import bcrypt
from sqlalchemy.orm import Session

from src.core.config import settings
from src.db.models import AccountDB
from src.db.session import SessionLocal
from src.domain.models import Account


class AccountService:
    def __init__(self, session_factory: Callable[[], Session] = SessionLocal) -> None:
        self._session_factory = session_factory

    @staticmethod
    def _validate_role(role: str) -> Literal["admin", "user"]:
        if role not in {"admin", "user"}:
            raise ValueError("Role must be either 'admin' or 'user'")
        return role  # type: ignore[return-value]

    @staticmethod
    def _to_domain(account_db: AccountDB) -> Account:
        return Account(
            account_id=account_db.account_id,
            password_hash=account_db.password_hash,
            role=AccountService._validate_role(account_db.role),
            email=account_db.email,
            phone=account_db.phone,
            full_name=account_db.full_name,
            account_type=account_db.account_type,
            token_limit=account_db.token_limit,
            token_used=account_db.token_used,
            plan_expires_at=account_db.plan_expires_at,
            tokens_reset_at=account_db.tokens_reset_at,
            created_at=account_db.created_at,
            updated_at=account_db.updated_at,
        )

    def create_account(
        self,
        password: str,
        email: str | None,
        phone: str | None,
        full_name: str | None = None,
        account_type: str = "normal",
        token_limit: int | None = None,
    ) -> Account:
        if email is None and phone is None:
            raise ValueError("Email or phone is required")
        if account_type not in {"normal", "plus", "pro"}:
            raise ValueError("Account type is invalid")
        with self._session_factory() as session:
            if email:
                email_taken = session.query(AccountDB).filter_by(email=email).first()
                if email_taken is not None:
                    raise ValueError("Email already exists")
            if phone:
                phone_taken = session.query(AccountDB).filter_by(phone=phone).first()
                if phone_taken is not None:
                    raise ValueError("Phone already exists")

            password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            now = datetime.now(timezone.utc)
            resolved_limit = self.resolve_token_limit(account_type, token_limit)
            plan_expires_at = self.get_plan_expiry(account_type)

            account_db = AccountDB(
                password_hash=password_hash,
                role="user",
                email=email,
                phone=phone,
                full_name=full_name,
                account_type=account_type,
                token_limit=resolved_limit,
                token_used=0,
                plan_expires_at=plan_expires_at,
                tokens_reset_at=now,
                updated_at=now,
            )
            session.add(account_db)
            session.commit()
            session.refresh(account_db)
            return self._to_domain(account_db)

    def get_account(self, account_id: int) -> Account:
        with self._session_factory() as session:
            account_db = session.get(AccountDB, account_id)
            if account_db is None:
                raise ValueError("Account not found")
            self._reset_tokens_if_needed(account_db)
            session.commit()
            return self._to_domain(account_db)

    def list_accounts(self, limit: int = 100, offset: int = 0) -> list[Account]:
        if limit < 1:
            raise ValueError("limit must be greater than 0")
        if offset < 0:
            raise ValueError("offset must be greater than or equal to 0")

        with self._session_factory() as session:
            accounts = session.query(AccountDB).offset(offset).limit(limit).all()
            return [self._to_domain(account_db) for account_db in accounts]

    def update_account(
        self,
        account_id: int,
        password: str | None = None,
        role: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        full_name: str | None = None,
        account_type: str | None = None,
        token_limit: int | None = None,
        plan_expires_at: datetime | None = None,
    ) -> Account:
        with self._session_factory() as session:
            account_db = session.get(AccountDB, account_id)
            if account_db is None:
                raise ValueError("Account not found")

            if password is not None:
                account_db.password_hash = bcrypt.hashpw(
                    password.encode("utf-8"),
                    bcrypt.gensalt(),
                ).decode("utf-8")

            if role is not None:
                account_db.role = self._validate_role(role)

            if full_name is not None:
                account_db.full_name = full_name

            if email is not None:
                if email != account_db.email:
                    email_taken = session.query(AccountDB).filter_by(email=email).first()
                    if email_taken is not None:
                        raise ValueError("Email already exists")
                account_db.email = email

            if phone is not None:
                if phone != account_db.phone:
                    phone_taken = session.query(AccountDB).filter_by(phone=phone).first()
                    if phone_taken is not None:
                        raise ValueError("Phone already exists")
                account_db.phone = phone

            if account_type is not None:
                if account_type not in {"normal", "plus", "pro"}:
                    raise ValueError("Account type is invalid")
                account_db.account_type = account_type

            if token_limit is not None:
                if token_limit < account_db.token_used:
                    raise ValueError("New token limit cannot be less than tokens already used")
                account_db.token_limit = token_limit

            if plan_expires_at is not None:
                account_db.plan_expires_at = plan_expires_at

            account_db.updated_at = datetime.now(timezone.utc)

            session.add(account_db)
            session.commit()
            session.refresh(account_db)
            return self._to_domain(account_db)

    def delete_account(self, account_id: int) -> None:
        with self._session_factory() as session:
            account_db = session.get(AccountDB, account_id)
            if account_db is None:
                raise ValueError("Account not found")

            session.delete(account_db)
            session.commit()

    def reserve_tokens(self, account_id: int, tokens: int) -> None:
        if tokens <= 0:
            raise ValueError("tokens must be greater than 0")

        with self._session_factory() as session:
            account_db = session.get(AccountDB, account_id)
            if account_db is None:
                raise ValueError("Account not found")
            self._reset_tokens_if_needed(account_db)
            if account_db.token_used + tokens > account_db.token_limit:
                raise ValueError("Token limit exceeded")

            account_db.token_used += tokens
            account_db.updated_at = datetime.now(timezone.utc)
            session.add(account_db)
            session.commit()

    def release_tokens(self, account_id: int, tokens: int) -> None:
        if tokens <= 0:
            raise ValueError("tokens must be greater than 0")

        with self._session_factory() as session:
            account_db = session.get(AccountDB, account_id)
            if account_db is None:
                raise ValueError("Account not found")
            if tokens > account_db.token_used:
                raise ValueError("Cannot release more tokens than currently used")

            account_db.token_used -= tokens
            account_db.updated_at = datetime.now(timezone.utc)
            session.add(account_db)
            session.commit()

    def get_account_by_identifier(self, identifier: str) -> Account:
        with self._session_factory() as session:
            account_db = (
                session.query(AccountDB)
                .filter((AccountDB.email == identifier) | (AccountDB.phone == identifier))
                .first()
            )
            if account_db is None:
                raise ValueError("Account not found")
            return self._to_domain(account_db)

    def resolve_token_limit(self, account_type: str, override_limit: int | None = None) -> int:
        if override_limit is not None:
            return override_limit
        if account_type == "plus":
            return settings.plus_token_limit
        if account_type == "pro":
            return settings.pro_token_limit
        return settings.normal_token_limit

    def get_plan_expiry(self, account_type: str) -> datetime | None:
        if account_type == "normal":
            return None
        now = datetime.now(timezone.utc)
        return now + settings.plan_duration

    def _reset_tokens_if_needed(self, account_db: AccountDB) -> None:
        now = datetime.now(timezone.utc)
        reset_at = account_db.tokens_reset_at
        if reset_at and reset_at > now:
            return
        if account_db.plan_expires_at and account_db.plan_expires_at < now:
            account_db.account_type = "normal"
            account_db.token_limit = settings.normal_token_limit
            account_db.plan_expires_at = None
        else:
            account_db.token_limit = self.resolve_token_limit(account_db.account_type)
        account_db.token_used = 0
        account_db.tokens_reset_at = now + settings.plan_duration
        account_db.updated_at = now
