from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from src.api.dependencies import get_orchestrator, require_roles
from src.schemas.upload import UploadResponse
from src.services.orchestration_service import EvaluationOrchestrator

router = APIRouter()


@router.post("", response_model=UploadResponse)
async def upload_problem(
    problem_file: UploadFile = File(...),
    essay_file: UploadFile = File(...),
    orchestrator: EvaluationOrchestrator = Depends(get_orchestrator),
    # _: dict = Depends(require_roles(["admin", "user"])),
) -> UploadResponse:
    try:
        data = "Problem:\n" + await orchestrator.extract_text(problem_file)
        data += "\n\nEssay:\n" + await orchestrator.extract_text(essay_file)
        file = UploadFile(filename=problem_file.filename, content_type="data"+problem_file.content_type, file=data.encode())
        await orchestrator.save_files(file)

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return UploadResponse(
        message="Files uploaded successfully",
        filename=problem_file.filename or "unknown",
        content_type=problem_file.content_type or "unknown"
    )

