from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from src.core.config import settings
from src.schemas.result import EvaluationResult
from src.services.account_service import AccountService
from src.services.ocr_service import OCRService
from src.services.parser_service import ParserService
from src.services.scoring_service import ScoringService

ALLOWED_DOCX_TYPES = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg"}


class EvaluationOrchestrator:
    def __init__(self, account_service: AccountService) -> None:
        self.account_service = account_service
        self.scoring_service = ScoringService()

    async def save_upload(self, upload_file: UploadFile) -> Path:
        upload_root = Path(settings.upload_dir)
        upload_root.mkdir(parents=True, exist_ok=True)

        safe_name = f"{uuid4()}_{upload_file.filename}"
        target = upload_root / safe_name
        content = await upload_file.read()
        target.write_bytes(content)
        await upload_file.seek(0)
        return target

    async def extract_text(self, upload_file: UploadFile) -> str:
        content_type = (upload_file.content_type or "").lower()
        raw = await upload_file.read()
        
        await upload_file.seek(0)

        if content_type in ALLOWED_DOCX_TYPES:
            return ParserService.parse_docx(raw)
        if content_type in ALLOWED_IMAGE_TYPES:
            return OCRService.extract_text_from_image(raw)
        raise ValueError("Unsupported file type")

    async def evaluate_submission(
        self,
        account_id: str,
        problem_file: UploadFile,
        essay_file: UploadFile,
    ) -> EvaluationResult:
        merge_text ="Problem:" + await self.extract_text(problem_file) + "\n"+ "Essay:" + "\n" + await self.extract_text(essay_file)

        estimated_tokens = ScoringService.estimate_tokens(text=merge_text)
        self.account_service.reserve_tokens(account_id=account_id, tokens=estimated_tokens)

        return self.scoring_service.evaluate(
            text=merge_text,
            estimated_tokens=estimated_tokens,
        )
