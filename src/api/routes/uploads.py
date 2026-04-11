from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from src.api.dependencies import get_orchestrator
from src.schemas.upload import UploadResponse
from src.services.orchestration_service import EvaluationOrchestrator

router = APIRouter()


@router.post("/problem", response_model=UploadResponse)
async def upload_problem(
    file: UploadFile = File(...),
    orchestrator: EvaluationOrchestrator = Depends(get_orchestrator),
) -> UploadResponse:
    try:
        await orchestrator.save_upload(file)
        await orchestrator.extract_text(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return UploadResponse(
        message="Problem uploaded successfully",
        filename=file.filename or "unknown",
        content_type=file.content_type or "unknown",
    )


@router.post("/essay", response_model=UploadResponse)
async def upload_essay(
    file: UploadFile = File(...),
    orchestrator: EvaluationOrchestrator = Depends(get_orchestrator),
) -> UploadResponse:
    try:
        await orchestrator.save_upload(file)
        await orchestrator.extract_text(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return UploadResponse(
        message="Essay uploaded successfully",
        filename=file.filename or "unknown",
        content_type=file.content_type or "unknown",
    )
