from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from src.core.config import settings
from src.schemas.result import EvaluationResult
from src.services.account_service import AccountService
from src.services.ocr_service import OCRService
from src.services.parser_service import ParserService
from src.services.scoring_writing_service import ScoringWritingService


ALLOWED_DOCX_TYPES = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg"}


class EvaluationOrchestrator:
    def __init__(self, account_service: AccountService) -> None:
        self.account_service = account_service
        self.scoring_service = ScoringWritingService()
        self.ocr_service = OCRService()

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
            return self.ocr_service.extract_text_from_image(raw)
        raise ValueError("Unsupported file type")

    async def _save_files_if_pro(self, account_id: int, problem_file: UploadFile, essay_file: UploadFile) -> None:
        account = self.account_service.get_account(account_id)
        if account.account_type != "pro":
            return
        await self.save_upload(problem_file)
        await problem_file.seek(0)
        await self.save_upload(essay_file)
        await essay_file.seek(0)

    async def evaluate_writing_submission(
        self,
        account_id: int,
        problem_file: UploadFile,
        essay_file: UploadFile,
        use_llm: bool = False,
    ) -> tuple[EvaluationResult, str, str]:
        problem_text = await self.extract_text(problem_file)
        essay_text = await self.extract_text(essay_file)
        input_llm = "Problem:" + problem_text + "\n" + "Essay:" + "\n" + essay_text
        input_model = problem_text + "[SEP]" + essay_text
        estimated_tokens = self.scoring_service.estimate_tokens(
            text=input_llm if use_llm else input_model,
            use_llm=use_llm,
        )
        self.account_service.reserve_tokens(account_id=account_id, tokens=estimated_tokens)
        await self._save_files_if_pro(account_id, problem_file, essay_file)
        if use_llm:
            return (
                self.scoring_service.llm_evaluate(
                    text=input_llm,
                    estimated_tokens=estimated_tokens,
                ),
                problem_text,
                essay_text,
            )
        return (
            self.scoring_service.model_evaluate(
                text=input_model,
                estimated_tokens=estimated_tokens,
            ),
            problem_text,
            essay_text,
        )
