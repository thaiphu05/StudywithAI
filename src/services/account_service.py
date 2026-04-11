from collections.abc import Callable

from sqlalchemy.orm import Session

from src.core.config import settings
from src.db.models import AccountDB
from src.db.session import SessionLocal
from src.domain.models import Account


class AccountService:
    def __init__(self, session_factory: Callable[[], Session] = SessionLocal) -> None:
        self._session_factory = session_factory

    @staticmethod
    def _to_domain(account_db: AccountDB) -> Account:
        return Account(
            account_id=account_db.account_id,
            email=account_db.email,
            token_limit=account_db.token_limit,
            token_used=account_db.token_used,
            created_at=account_db.created_at,
        )

    def create_account(self, account_id: str, email: str | None, token_limit: int | None) -> Account:
        with self._session_factory() as session:
            existing = session.get(AccountDB, account_id)
            if existing is not None:
                raise ValueError("Account already exists")

            account_db = AccountDB(
                account_id=account_id,
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

    def reserve_tokens(self, account_id: str, tokens: int) -> None:
        with self._session_factory() as session:
            account_db = session.get(AccountDB, account_id)
            if account_db is None:
                raise ValueError("Account not found")
            if account_db.token_used + tokens > account_db.token_limit:
                raise ValueError("Token limit exceeded")

            account_db.token_used += tokens
            session.add(account_db)
            session.commit()
