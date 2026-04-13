import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.core.config import settings
from src.services.account_service import AccountService
from src.services.auth_service import AuthService
from src.services.orchestration_service import EvaluationOrchestrator

account_service = AccountService()
auth_service = AuthService()
orchestrator = EvaluationOrchestrator(account_service=account_service)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")



def get_account_service() -> AccountService:
    return account_service


def get_orchestrator() -> EvaluationOrchestrator:
    return orchestrator


def get_auth_service() -> AuthService:
    return auth_service


def validate_token(token: str = Depends(oauth2_scheme)) -> dict:
    if not settings.secret_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SECRET_KEY is not configured",
        )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        account_id = payload.get("sub")
        token_role = payload.get("role")
        if not account_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if token_role is not None and token_role not in {"admin", "user"}:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return payload


def require_roles(allowed_roles: list[str]):
    def dependency(payload: dict = Depends(validate_token)) -> dict:
        role = payload.get("role")
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden for this account",
            )
        return payload
    return dependency
