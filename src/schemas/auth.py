from pydantic import BaseModel

class LoginRequest(BaseModel):
    identifier: str
    password: str

class LoginResponse(BaseModel):
    auth_token: str
    account_id: int
