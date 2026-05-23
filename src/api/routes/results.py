from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from src.api.dependencies import get_account_service, get_orchestrator, require_roles
from src.schemas.result import EvaluationResult
from src.services.account_service import AccountService
from src.services.orchestration_service import EvaluationOrchestrator

router = APIRouter()


@router.post("/writing/{account_id}", response_model=EvaluationResult)
async def evaluate_writing(
    account_id: int,
    problem_file: UploadFile = File(...),
    essay_file: UploadFile = File(...),
    orchestrator: EvaluationOrchestrator = Depends(get_orchestrator),
    account_service: AccountService = Depends(get_account_service),
    token_payload: dict = Depends(require_roles(["admin", "user"])),
) -> EvaluationResult:
    if account_id != token_payload.get("sub"):
        raise HTTPException(status_code=403, detail="Forbidden for this account")

    try:
        account = account_service.get_account(account_id)
        use_llm = account.account_type == "pro"
        return await orchestrator.evaluate_writing_submission(
            account_id=account_id,
            problem_file=problem_file,
            essay_file=essay_file,
            use_llm=use_llm,
        )
    except ValueError as exc:
        message = str(exc)
        if message == "Account not found":
            raise HTTPException(status_code=404, detail=message) from exc
        if message == "Token limit exceeded":
            raise HTTPException(status_code=402, detail=message) from exc
        raise HTTPException(status_code=400, detail=message) from exc

# @router.post("/speaking/{account_id}", response_model=EvaluationResult)
# async def evaluate_speaking
