from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, Optional


@dataclass
class Account:
    account_id: int
    password_hash: str
    role: Literal["admin", "user"] = "user"
    email: Optional[str] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    account_type: Literal["normal", "plus", "pro"] = "normal"
    token_limit: int = 10000
    token_used: int = 0
    plan_expires_at: Optional[datetime] = None
    tokens_reset_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class StudyHistory:
    id: int
    account_id: int
    history_type: Literal["writing", "speaking"]
    payload: dict
    created_at: datetime


@dataclass
class EvaluationJob:
    job_id: str
    account_id: int
    prompt_text: str
    essay_text: str
    estimated_tokens: int
    created_at: datetime = field(default_factory=datetime.utcnow)
