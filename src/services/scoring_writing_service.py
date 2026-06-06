from pathlib import Path

import torch

from src.core.config import settings
from src.schemas.result import EvaluationResult
from src.models.LLM_model import LLMModel
from src.models.WR_model import WR_Model
from src.utils.llm import split_output
from src.utils.writing import format_writing_model_output


class ScoringWritingService:
    def __init__(self):
        self.llm_model = LLMModel()
        model_path = Path(settings.writing_model_path)
        if not model_path.exists():
            raise FileNotFoundError(
                f"Writing model checkpoint not found: {model_path}. "
                "Set WRITING_MODEL_PATH in .env or update settings.writing_model_path."
            )
        wr_model = WR_Model()
        self.model, self.tokenizer = wr_model.load_model(path=str(model_path))
    @staticmethod
    def estimate_tokens(text: str, use_llm: bool = False) -> int:
        if use_llm:
            return max(1, len(text)) // 2
        return max(1, len(text)) // 4
    
    def model_evaluate(self, text: str, estimated_tokens: int) -> EvaluationResult:
        self.model.eval()
        data = self.tokenizer(text=text,add_special_tokens=True,
                            padding='max_length',
                            truncation='longest_first',
                            max_length=1024,
                            return_attention_mask=True)
        
        test_input_ids = data['input_ids']
        test_masks = data['attention_mask']
        test_input_ids_tensor = torch.tensor(test_input_ids).unsqueeze(0).to("cpu")
        test_masks_tensor = torch.tensor(test_masks).unsqueeze(0).to("cpu")
        out = self.model(test_input_ids_tensor, test_masks_tensor)
        predicted_scaled = (out.cpu().detach().numpy() * 2).round() / 2
        return format_writing_model_output(
            predicted_scaled=predicted_scaled,
            estimated_tokens=estimated_tokens,
        )
        
    def llm_evaluate(self, text: str, estimated_tokens: int) -> EvaluationResult:
        instruction_prompt = (
            """
Role: Act as a professional IELTS Writing Task 2 Examiner.

Input Data: User will provide two parts:
    Topic (Problem): The specific question or statement to be addressed.
    Essay: The candidate's written response.
Task: Evaluate the essay in detail. You MUST cross-reference the essay's content with the specific requirements of the Topic to accurately assess the "Task Achievement" score (e.g., did the writer address all parts of the prompt? is the position relevant to the question?).

Output Formatting Rules (Strictly Follow):
    DO NOT include any introductory remarks, greetings, or conversational filler.
    DO NOT include any concluding remarks.
    FORMAT: Use the exact structure below:

Task Achievement:
    Comments: [Analyze how well the essay addresses the specific requirements of the Topic. Evaluate the relevance and development of ideas in direct response to the prompt.]
    Examples: [Direct quotes or specific references from the text]
    Suggested Band Score: [Score]

Coherence and Cohesion:
    Comments: [Analysis of organization, logical flow, and cohesive devices]
    Examples: [List of linking words and paragraphing techniques]
    Suggested Band Score: [Score]

Lexical Resource:
    Comments: [Analysis of vocabulary range, precision, and stylistic Appropriateness]
    Examples: [List of good collocations and specific errors]
    Suggested Band Score: [Score]

Grammatical Range and Accuracy:
    Comments: [Analysis of sentence structures and error frequency]
    Examples: [List of complex structures and specific grammatical errors]
    Suggested Band Score: [Score]

Overall Band Score: [Calculated Score]

General Feedback:
    Strengths: [Bullet points]
    Areas for Improvement: [Bullet points]
    Suggestions for Enhancement: [Bullet points]"""
            + text
        )
        
        llm_result = self.llm_model.evaluate(instruction_prompt)
        criteria, overall_band, summary = split_output(llm_result)

        return EvaluationResult(
            overall_band=overall_band,
            summary=summary,
            criteria=criteria,
            estimated_tokens_used=estimated_tokens,
        )
