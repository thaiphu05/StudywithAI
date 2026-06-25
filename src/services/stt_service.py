from src.core.config import settings
from src.models.STT_model import STTModel


class STTService:
    def __init__(self) -> None:
        self.model = STTModel(model_size=settings.stt_model_size)
        self.model.load_model()

    def transcribe(self, audio: bytes) -> dict:
        return self.model.transcribe(audio)
