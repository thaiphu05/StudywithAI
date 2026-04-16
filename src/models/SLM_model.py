import google.generativeai as genai
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch 

from src.core.config import settings 

class SLMModel:
    def __init__(self, model_name: str = "gemini-2.0-flash", self_host: bool = False) -> None:
        self.model_name = model_name
        self.self_host = self_host
        self.model = None
        self.tokenizer = None
        self.api_configured = False

    def _setup_api(self):
        if not self.api_configured:
            genai.configure(api_key=settings.llm_api_key) 
            self.api_configured = True

    def load_model(self) -> None:
        if self.self_host:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name, 
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto"
            )
        else:
            self._setup_api()
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={"max_output_tokens": 1024}
            )

    def generate_text(self, prompt: str, max_length: int = 50) -> str:
        if self.model is None:
            self.load_model()

        if self.self_host:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            outputs = self.model.generate(**inputs, max_new_tokens=max_length)
            return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        else:
            response = self.model.generate_content(prompt)
            return response.text

    def evaluate(self, prompt: str) -> str:
        return self.generate_text(prompt)