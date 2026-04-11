from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from src.api.dependencies import get_orchestrator
from src.schemas.result import EvaluationResult
from src.services.orchestration_service import EvaluationOrchestrator

router = APIRouter()


@router.post("/evaluate", response_model=EvaluationResult)
async def evaluate(
    account_id: str = Form(...),
    problem_file: UploadFile = File(...),
    essay_file: UploadFile = File(...),
    orchestrator: EvaluationOrchestrator = Depends(get_orchestrator),
) -> EvaluationResult:
    try:
        return await orchestrator.evaluate_submission(
            account_id=account_id,
            prompt_file=problem_file,
            essay_file=essay_file,
        )
    except ValueError as exc:
        message = str(exc)
        if message == "Account not found":
            raise HTTPException(status_code=404, detail=message) from exc
        if message == "Token limit exceeded":
            raise HTTPException(status_code=402, detail=message) from exc
        raise HTTPException(status_code=400, detail=message) from exc
