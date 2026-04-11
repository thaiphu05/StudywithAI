import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.core.config import settings
from src.domain.models import Account
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


def get_current_account(
    token: str = Depends(oauth2_scheme),
    account_service: AccountService = Depends(get_account_service),
) -> Account:
    if not settings.secret_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SECRET_KEY is not configured",
        )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        account_id = payload.get("sub")
        if not account_id:
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

    try:
        return account_service.get_account(account_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc