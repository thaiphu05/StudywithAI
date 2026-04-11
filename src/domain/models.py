from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Account:
    account_id: str
    username: str
    password_hash: str
    email: Optional[str] = None
    token_limit: int = 200000
    token_used: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EvaluationJob:
    job_id: str
    account_id: str
    prompt_text: str
    essay_text: str
    estimated_tokens: int
    created_at: datetime = field(default_factory=datetime.utcnow)
