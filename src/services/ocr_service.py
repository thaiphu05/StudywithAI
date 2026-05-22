from io import BytesIO

from fastapi import UploadFile
from PIL import Image

from src.models.OCR_model import OCRModel
from src.utils.image import postprocessing, preprocessing

class OCRService:
    def __init__(self) -> None:
        self.ocr_model = OCRModel()
        self.ocr_model.load_model()

    def extract_text_from_image(self, raw: bytes) -> str:
        image = Image.open(BytesIO(raw))
        image = preprocessing(image)
        ocr_text = self.ocr_model.extract_text(image)
        return postprocessing(ocr_text)
