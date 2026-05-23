from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import get_account_service, require_roles
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
            password=payload.password,
            email=payload.email,
            phone=payload.phone,
            full_name=payload.full_name,
            account_type=payload.account_type,
            token_limit=payload.token_limit,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return AccountResponse(
        account_id=account.account_id,
        role=account.role,
        email=account.email,
        phone=account.phone,
        full_name=account.full_name,
        account_type=account.account_type,
        token_limit=account.token_limit,
        token_used=account.token_used,
    )


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(
    account_id: int,
    account_service: AccountService = Depends(get_account_service),
    token_payload: dict = Depends(require_roles(["admin", "user"])),
) -> AccountResponse:
    if token_payload.get("role") != "admin" and account_id != token_payload.get("sub"):
        raise HTTPException(status_code=403, detail="Forbidden for this account")
    try:
        account = account_service.get_account(account_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return AccountResponse(
        account_id=account.account_id,
        role=account.role,
        email=account.email,
        phone=account.phone,
        full_name=account.full_name,
        account_type=account.account_type,
        token_limit=account.token_limit,
        token_used=account.token_used,
    )
