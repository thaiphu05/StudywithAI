from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import get_history_service, require_roles
from src.schemas.history import HistoryCreateRequest, HistoryListResponse, HistoryResponse
from src.services.history_service import HistoryService

router = APIRouter()


@router.post("", response_model=HistoryResponse)
def create_history(
    payload: HistoryCreateRequest,
    history_service: HistoryService = Depends(get_history_service),
    token_payload: dict = Depends(require_roles(["admin", "user"])),
) -> HistoryResponse:
    account_id = token_payload.get("sub")
    try:
        history = history_service.create_history(
            account_id=account_id,
            history_type=payload.history_type,
            payload=payload.payload,
        )
    except ValueError as exc:
        message = str(exc)
        if message == "History limit exceeded":
            raise HTTPException(status_code=409, detail=message) from exc
        if message == "Account not found":
            raise HTTPException(status_code=404, detail=message) from exc
        raise HTTPException(status_code=400, detail=message) from exc

    return HistoryResponse(
        id=history.id,
        account_id=history.account_id,
        history_type=history.history_type,
        payload=history.payload,
        created_at=history.created_at,
    )


@router.get("", response_model=HistoryListResponse)
def list_history(
    history_type: str | None = None,
    limit: int = 20,
    offset: int = 0,
    history_service: HistoryService = Depends(get_history_service),
    token_payload: dict = Depends(require_roles(["admin", "user"])),
) -> HistoryListResponse:
    account_id = token_payload.get("sub")
    try:
        items, total = history_service.list_history(
            account_id=account_id,
            history_type=history_type,  # type: ignore[arg-type]
            limit=limit,
            offset=offset,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return HistoryListResponse(
        items=[
            HistoryResponse(
                id=item.id,
                account_id=item.account_id,
                history_type=item.history_type,
                payload=item.payload,
                created_at=item.created_at,
            )
            for item in items
        ],
        total=total,
    )


@router.get("/{history_id}", response_model=HistoryResponse)
def get_history(
    history_id: int,
    history_service: HistoryService = Depends(get_history_service),
    token_payload: dict = Depends(require_roles(["admin", "user"])),
) -> HistoryResponse:
    account_id = token_payload.get("sub")
    try:
        history = history_service.get_history(account_id=account_id, history_id=history_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return HistoryResponse(
        id=history.id,
        account_id=history.account_id,
        history_type=history.history_type,
        payload=history.payload,
        created_at=history.created_at,
    )


@router.delete("/{history_id}")
def delete_history(
    history_id: int,
    history_service: HistoryService = Depends(get_history_service),
    token_payload: dict = Depends(require_roles(["admin", "user"])),
) -> dict:
    account_id = token_payload.get("sub")
    try:
        history_service.delete_history(account_id=account_id, history_id=history_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"message": "History deleted"}
