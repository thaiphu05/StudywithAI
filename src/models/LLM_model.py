import google.generativeai as genai

import torch 

from src.core.config import settings 

class LLMModel:
    def __init__(self, model_name: str = "gemini-2.5-flash") -> None:
        self.model_name = model_name

    def load_model(self) -> None:
        genai.configure(api_key=settings.llm_api_key) 
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={"max_output_tokens": 8192}
        )

    def generate_text(self, prompt: str) -> str:
        self.load_model()

        response = self.model.generate_content(prompt)
        return response.text

    def evaluate(self, prompt: str) -> str:
        return self.generate_text(prompt)