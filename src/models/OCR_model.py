
import os
from typing import Optional

from paddleocr import PaddleOCR
from PIL import Image

from src.core.config import settings



class OCRModel:
    def __init__(self, self_host: bool | None = None, lang: str | None = None) -> None:
        self.self_host = settings.ocr_self_host if self_host is None else self_host
        self.lang = lang or "en"
        self.model: Optional[PaddleOCR] = None
        self.ocr_api = None

    def load_model(self) -> None:
        if self.self_host:
            self.model = PaddleOCR(use_angle_cls=True, lang=self.lang)
        else:
            self.ocr_api = os.getenv("OCR_API_KEY")

    def extract_text(self, image: Image.Image) -> str:
        if self.self_host:
            if self.model is None:
                raise RuntimeError("OCR model is not loaded")
            result = self.model.ocr(image, cls=True)
            lines: list[str] = []
            for page in result:
                for line in page:
                    lines.append(line[1][0])
            return "\n".join(lines).strip()

        # Placeholder implementation for API-based OCR
        return "OCR text from API"
