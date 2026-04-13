
import os
from transformers import AutoModel

from PIL import Image
from pydantic import BaseModel  
from src.core.config import settings



class OCRModel:
    def __init__(self, self_host: bool | None = None, model_name: str | None = None) -> None:
        self.self_host = settings.ocr_self_host if self_host is None else self_host
        self.model = None
        self.model_name = model_name
        self.ocr_api = None
        

    def load_model(self) -> None:
        if self.self_host:
            self.model = AutoModel.from_pretrained(self.model_name)
        else:
            self.ocr_api = os.getenv("OCR_API_KEY")

    def extract_text(self, image: Image.Image) -> str:
        output = ""
        if self.self_host:
            output = self.model.predict(image)
        else:
            # Placeholder implementation for API-based OCR
            output = "OCR text from API"
        return output