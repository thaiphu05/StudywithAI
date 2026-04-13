import bcrypt
import jwt
from datetime import datetime, timedelta, timezone

from src.core.config import settings
from src.services.account_service import AccountService


class AuthService:
    def __init__(self) -> None:
        self.secret_key = settings.secret_key
        self.access_token_expire_minutes = settings.access_token_expire_minutes

    def login(self, username: str, password: str) -> tuple[str, str]:
        if not self.secret_key:
            raise RuntimeError("SECRET_KEY is not configured")

        account_service = AccountService()
        account = account_service.get_account_by_username(username)

        password_ok = bcrypt.checkpw(
            password.encode("utf-8"),
            account.password_hash.encode("utf-8"),
        )
        if not password_ok:
            raise ValueError("Invalid username or password")

        payload = {
            "sub": account.account_id,
            "role": account.role,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes),
        }
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        return token, account.account_id
    
