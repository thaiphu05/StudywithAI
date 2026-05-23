from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class HistoryCreateRequest(BaseModel):
    history_type: Literal["writing", "speaking"]
    payload: dict[str, Any]


class HistoryResponse(BaseModel):
    id: int
    account_id: int
    history_type: Literal["writing", "speaking"]
    payload: dict[str, Any]
    created_at: datetime


class HistoryListResponse(BaseModel):
    items: list[HistoryResponse]
    total: int
