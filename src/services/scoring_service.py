from src.schemas.result import EvaluationResult
from src.models.SLM_model import SLMModel
from src.utils.slm import split_output


class ScoringService:
    def __init__(self):
        self.slm_model = SLMModel()

    @staticmethod
    def estimate_tokens(prompt_text: str, essay_text: str) -> int:
        # Approximation: 1 token ~= 4 chars for English prose.
        return max(1, (len(prompt_text) + len(essay_text)) // 4)

    def evaluate(self, essay_text: str, estimated_tokens: int) -> EvaluationResult:
        # Use the SLM model to get the actual evaluation
        instruction_prompt = (
            """You are an IELTS Writing Task 2 examiner.
Evaluate the essay below in detail according to the four official IELTS Writing criteria: Task Achievement, Coherence and Cohesion, Lexical Resource, and Grammatical Range and Accuracy.
For each criterion, provide specific comments, examples, and a suggested band score.
Then, provide an Overall Band Score and general feedback including Strengths, Areas for Improvement, and Suggestions for Enhancement.
Essay:
"""
            + essay_text
        )
        
        slm_result = self.slm_model.evaluate(instruction_prompt)
        criteria, overall_band, summary = split_output(slm_result)

        return EvaluationResult(
            overall_band=overall_band,
            summary=summary,
            criteria=criteria,
            estimated_tokens_used=estimated_tokens,
        )
