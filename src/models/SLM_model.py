from transformer import AutoModelForCasualLM, AutoTokenizer
import os

class SLMModel:
    def __init__(self, model_name: str = "gpt2", self_host: bool | None = None) -> None:
        self.model_name = model_name
        self.model = None
        self.llm_api = None
        self.tokenizer = None
        self.self_host = self_host 

    def load_model(self) -> None:
        if self.self_host:
            self.model = AutoModelForCasualLM.from_pretrained(self.model_name)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        else:
            self.llm_api = os.getenv("LLM_API_KEY")

    def generate_text(self, prompt: str, max_length: int = 50) -> str:
        if self.self_host:
            inputs = self.tokenizer(prompt, return_tensors="pt")
            outputs = self.model.generate(**inputs, max_length=max_length)
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        else:
            # Placeholder implementation for API-based LLM
            generated_text = "Generated text from API"
        return generated_text