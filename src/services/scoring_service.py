from src.schemas.result import EvaluationResult
from src.models.SLM_model import SLMModel
from src.utils.slm import split_output


class ScoringService:
    def __init__(self):
        self.slm_model = SLMModel()

    @staticmethod
    def estimate_tokens(text: str) -> int:
        return max(1, len(text)) // 4

    def evaluate(self, text: str, estimated_tokens: int) -> EvaluationResult:
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
        
        slm_result = self.slm_model.evaluate(instruction_prompt)
        criteria, overall_band, summary = split_output(slm_result)

        return EvaluationResult(
            overall_band=overall_band,
            summary=summary,
            criteria=criteria,
            estimated_tokens_used=estimated_tokens,
        )
