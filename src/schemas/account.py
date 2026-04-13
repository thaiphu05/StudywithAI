from typing import Literal

from pydantic import BaseModel, EmailStr


class CreateAccountRequest(BaseModel):
    account_id: str
    username: str
    password: str
    role : Literal["admin", "user"] = "user"
    email: EmailStr | None = None
    token_limit: int | None = None


class AccountResponse(BaseModel):
    account_id: str
    username: str
    role: Literal["admin", "user"]
    email: EmailStr | None = None
    token_limit: int
    token_used: int
