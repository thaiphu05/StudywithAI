from typing import Literal

from pydantic import BaseModel, EmailStr


class CreateAccountRequest(BaseModel):
    email: EmailStr | None = None
    phone: str | None = None
    password: str
    role: Literal["admin", "user"] = "user"
    account_type: Literal["normal", "plus", "pro"] = "normal"
    full_name: str | None = None
    token_limit: int | None = None

    def model_post_init(self, __context) -> None:  # type: ignore[override]
        if self.email is None and self.phone is None:
            raise ValueError("email or phone is required")


class AccountResponse(BaseModel):
    account_id: int
    role: Literal["admin", "user"]
    email: EmailStr | None = None
    phone: str | None = None
    full_name: str | None = None
    account_type: Literal["normal", "plus", "pro"]
    token_limit: int
    token_used: int
