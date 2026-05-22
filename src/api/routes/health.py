from fastapi import APIRouter, Depends
from src.api.dependencies import require_roles


router = APIRouter()


@router.get("")
def health_check(token_payload: dict = Depends(require_roles(["admin"]))) -> dict[str, str]:
    
    return {"status": "ok"}
