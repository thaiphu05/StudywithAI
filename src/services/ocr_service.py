from src.models.OCR_model import OCRModel
from PIL import Image 
from src.utils.image import *

class OCRService:
    def __init__ (self):
        self.OCRModel = OCRModel()
        self.OCRModel.load_model()
        
    @staticmethod
    def extract_text_from_image(self, image_path : str) -> str:
        # Placeholder for OCR provider integration (Tesseract, Vision API, etc.).
        image = Image.open(image_path)
        image = preprocessing(image)  
        OCR_text = self.OCRModel.extract_text(image)
        OCR_text = postprocessing(OCR_text)
        return "[OCR text placeholder]" + OCR_text
