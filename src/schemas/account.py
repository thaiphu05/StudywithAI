from pydantic import BaseModel, EmailStr


class CreateAccountRequest(BaseModel):
    account_id: str
    username: str
    password: str
    email: EmailStr | None = None
    token_limit: int | None = None


class AccountResponse(BaseModel):
    account_id: str
    username: str
    email: EmailStr | None = None
    token_limit: int
    token_used: int
