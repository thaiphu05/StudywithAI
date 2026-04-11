from src.schemas.result import CriterionFeedback, EvaluationResult


class ScoringService:
    @staticmethod
    def estimate_tokens(prompt_text: str, essay_text: str) -> int:
        # Approximation: 1 token ~= 4 chars for English prose.
        return max(1, (len(prompt_text) + len(essay_text)) // 4)

    @staticmethod
    def evaluate(prompt_text: str, essay_text: str, estimated_tokens: int) -> EvaluationResult:
        _ = (prompt_text, essay_text)

        criteria = [
            CriterionFeedback(
                criterion="Task Response",
                band=6.5,
                explanation="Addresses the prompt but could expand key arguments.",
            ),
            CriterionFeedback(
                criterion="Coherence and Cohesion",
                band=6.0,
                explanation="Logical progression is clear, though linking can be tighter.",
            ),
            CriterionFeedback(
                criterion="Lexical Resource",
                band=6.5,
                explanation="Vocabulary range is adequate with minor repetition.",
            ),
            CriterionFeedback(
                criterion="Grammatical Range and Accuracy",
                band=6.0,
                explanation="Uses mixed structures with occasional grammatical errors.",
            ),
        ]

        return EvaluationResult(
            overall_band=6.25,
            summary="This is a baseline scaffold score. Replace with your real scoring model.",
            criteria=criteria,
            estimated_tokens_used=estimated_tokens,
        )
