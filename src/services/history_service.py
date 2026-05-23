from collections.abc import Callable
from datetime import datetime, timezone
from typing import Literal

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from src.db.models import AccountDB
from src.db.models import StudyHistoryDB
from src.db.session import SessionLocal
from src.domain.models import StudyHistory


class HistoryService:
    def __init__(self, session_factory: Callable[[], Session] = SessionLocal) -> None:
        self._session_factory = session_factory

    @staticmethod
    def _to_domain(history_db: StudyHistoryDB) -> StudyHistory:
        return StudyHistory(
            id=history_db.id,
            account_id=history_db.account_id,
            history_type=history_db.history_type,  # type: ignore[arg-type]
            payload=history_db.payload,
            created_at=history_db.created_at,
        )

    @staticmethod
    def _plan_limit(account_type: str) -> int:
        if account_type == "plus":
            return 10
        if account_type == "pro":
            return 100
        return 3

    def create_history(
        self,
        account_id: int,
        history_type: Literal["writing", "speaking"],
        payload: dict,
    ) -> StudyHistory:
        with self._session_factory() as session:
            account = session.get(AccountDB, account_id)
            if account is None:
                raise ValueError("Account not found")

            limit = self._plan_limit(account.account_type)
            if account.account_type == "pro":
                count = session.scalar(
                    select(func.count(StudyHistoryDB.id)).where(StudyHistoryDB.account_id == account_id)
                )
                if count is not None and count >= limit:
                    raise ValueError("History limit exceeded")

            history_db = StudyHistoryDB(
                account_id=account_id,
                history_type=history_type,
                payload=payload,
                created_at=datetime.now(timezone.utc),
            )
            session.add(history_db)
            session.flush()

            if account.account_type in {"normal", "plus"}:
                subquery = (
                    select(StudyHistoryDB.id)
                    .where(StudyHistoryDB.account_id == account_id)
                    .order_by(StudyHistoryDB.created_at.desc())
                    .offset(limit)
                )
                session.execute(delete(StudyHistoryDB).where(StudyHistoryDB.id.in_(subquery)))

            session.commit()
            session.refresh(history_db)
            return self._to_domain(history_db)

    def list_history(
        self,
        account_id: int,
        history_type: Literal["writing", "speaking"] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[StudyHistory], int]:
        if limit < 1:
            raise ValueError("limit must be greater than 0")
        if offset < 0:
            raise ValueError("offset must be greater than or equal to 0")

        with self._session_factory() as session:
            query = select(StudyHistoryDB).where(StudyHistoryDB.account_id == account_id)
            if history_type:
                query = query.where(StudyHistoryDB.history_type == history_type)
            query = query.order_by(StudyHistoryDB.created_at.desc())

            total_query = select(func.count(StudyHistoryDB.id)).where(StudyHistoryDB.account_id == account_id)
            if history_type:
                total_query = total_query.where(StudyHistoryDB.history_type == history_type)

            total = session.scalar(total_query) or 0
            items = session.scalars(query.offset(offset).limit(limit)).all()
            return [self._to_domain(item) for item in items], total

    def get_history(self, account_id: int, history_id: int) -> StudyHistory:
        with self._session_factory() as session:
            history_db = session.get(StudyHistoryDB, history_id)
            if history_db is None or history_db.account_id != account_id:
                raise ValueError("History not found")
            return self._to_domain(history_db)

    def delete_history(self, account_id: int, history_id: int) -> None:
        with self._session_factory() as session:
            history_db = session.get(StudyHistoryDB, history_id)
            if history_db is None or history_db.account_id != account_id:
                raise ValueError("History not found")
            session.delete(history_db)
            session.commit()
