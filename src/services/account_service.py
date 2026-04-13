from collections.abc import Callable
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
            username=account_db.username,
            password_hash=account_db.password_hash,
            role=AccountService._validate_role(account_db.role),
            email=account_db.email,
            token_limit=account_db.token_limit,
            token_used=account_db.token_used,
            created_at=account_db.created_at,
        )

    def create_account(
        self,
        account_id: str,
        username: str,
        password: str,
        email: str | None,
        token_limit: int | None,
    ) -> Account:
        with self._session_factory() as session:
            existing = session.get(AccountDB, account_id)
            if existing is not None:
                raise ValueError("Account already exists")
            username_taken = session.query(AccountDB).filter_by(username=username).first()
            if username_taken is not None:
                raise ValueError("Username already exists")

            password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

            account_db = AccountDB(
                account_id=account_id,
                username=username,
                password_hash=password_hash,
                role="user",
                email=email,
                token_limit=token_limit if token_limit is not None else settings.default_token_limit,
                token_used=0,
            )
            session.add(account_db)
            session.commit()
            session.refresh(account_db)
            return self._to_domain(account_db)

    def get_account(self, account_id: str) -> Account:
        with self._session_factory() as session:
            account_db = session.get(AccountDB, account_id)
            if account_db is None:
                raise ValueError("Account not found")
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
        account_id: str,
        username: str | None = None,
        password: str | None = None,
        role: str | None = None,
        email: str | None = None,
        token_limit: int | None = None,
    ) -> Account:
        with self._session_factory() as session:
            account_db = session.get(AccountDB, account_id)
            if account_db is None:
                raise ValueError("Account not found")

            if username is not None and username != account_db.username:
                username_taken = session.query(AccountDB).filter_by(username=username).first()
                if username_taken is not None:
                    raise ValueError("Username already exists")
                account_db.username = username

            if password is not None:
                account_db.password_hash = bcrypt.hashpw(
                    password.encode("utf-8"),
                    bcrypt.gensalt(),
                ).decode("utf-8")

            if role is not None:
                account_db.role = self._validate_role(role)

            if email is not None:
                account_db.email = email

            if token_limit is not None:
                if token_limit < account_db.token_used:
                    raise ValueError("New token limit cannot be less than tokens already used")
                account_db.token_limit = token_limit

            session.add(account_db)
            session.commit()
            session.refresh(account_db)
            return self._to_domain(account_db)

    def delete_account(self, account_id: str) -> None:
        with self._session_factory() as session:
            account_db = session.get(AccountDB, account_id)
            if account_db is None:
                raise ValueError("Account not found")

            session.delete(account_db)
            session.commit()

    def reserve_tokens(self, account_id: str, tokens: int) -> None:
        if tokens <= 0:
            raise ValueError("tokens must be greater than 0")

        with self._session_factory() as session:
            account_db = session.get(AccountDB, account_id)
            if account_db is None:
                raise ValueError("Account not found")
            if account_db.token_used + tokens > account_db.token_limit:
                raise ValueError("Token limit exceeded")

            account_db.token_used += tokens
            session.add(account_db)
            session.commit()

    def release_tokens(self, account_id: str, tokens: int) -> None:
        if tokens <= 0:
            raise ValueError("tokens must be greater than 0")

        with self._session_factory() as session:
            account_db = session.get(AccountDB, account_id)
            if account_db is None:
                raise ValueError("Account not found")
            if tokens > account_db.token_used:
                raise ValueError("Cannot release more tokens than currently used")

            account_db.token_used -= tokens
            session.add(account_db)
            session.commit()

    def get_account_by_username(self, username: str) -> Account:
        with self._session_factory() as session:
            account_db = (
                session.query(AccountDB)
                .filter(AccountDB.username == username).first()
            )
            if account_db is None:
                raise ValueError("Account not found")
            return self._to_domain(account_db)
