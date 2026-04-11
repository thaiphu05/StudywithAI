from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import get_account_service, get_current_account
from src.domain.models import Account
from src.schemas.account import AccountResponse, CreateAccountRequest
from src.services.account_service import AccountService

router = APIRouter()


@router.post("", response_model=AccountResponse)
def create_account(
    payload: CreateAccountRequest,
    account_service: AccountService = Depends(get_account_service),
) -> AccountResponse:
    try:
        account = account_service.create_account(
            account_id=payload.account_id,
            username=payload.username,
            password=payload.password,
            email=payload.email,
            token_limit=payload.token_limit,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return AccountResponse(
        account_id=account.account_id,
        username=account.username,
        email=account.email,
        token_limit=account.token_limit,
        token_used=account.token_used,
    )


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(
    account_id: str,
    account_service: AccountService = Depends(get_account_service),
    current_account: Account = Depends(get_current_account),

) -> AccountResponse:
    if account_id != current_account.account_id:
        raise HTTPException(status_code=403, detail="Forbidden for this account")
    try:
        account = account_service.get_account(account_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return AccountResponse(
        account_id=account.account_id,
        username=account.username,
        email=account.email,
        token_limit=account.token_limit,
        token_used=account.token_used,
    )
