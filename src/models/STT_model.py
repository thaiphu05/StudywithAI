import os
from transformers import AutoModel

from pydantic import BaseModel  
from src.core.config import settings

class STTModel:
    def __init__(self, self_host: bool | None = None, model_name: str | None = None) -> None:
        self.self_host = settings.stt_self_host if self_host is None else self_host
        self.model = None
        self.model_name = model_name
        self.stt_api = None
        

    def load_model(self) -> None:
        if self.self_host:
            self.model = AutoModel.from_pretrained(self.model_name)
        else:
            self.stt_api = os.getenv("STT_API_KEY")

    def transcribe_audio(self, audio_file: bytes) -> str:
        output = ""
        if self.self_host:
            output = self.model.predict(audio_file)
        else:
            output = "Transcribed text from API"
        return output
