from src.models.STT_model import STTModel
from src.utils.image import *

class STTService:
    def __init__ (self):
        self.STTModel = STTModel()
        self.STTModel.load_model()
        
    @staticmethod
    def transcribe_audio(self, audio: bytes) -> str:
        return self.STTModel.transcribe_audio(audio)
