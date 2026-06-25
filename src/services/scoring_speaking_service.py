from src.models.LLM_model import LLMModel
from src.schemas.result import CriterionFeedback, EvaluationResult
from src.services.stt_service import STTService
from src.utils.llm import split_output


class ScoringSpeakingService:
    def __init__(self) -> None:
        self.llm_model = LLMModel()
        self.stt_service = STTService()

    @staticmethod
    def estimate_tokens(text: str) -> int:
        return max(1, len(text)) // 2

    def evaluate_from_audio(
        self,
        audio: bytes,
        topic: str = "",
    ) -> EvaluationResult:
        stt_result = self.stt_service.transcribe(audio)
        transcription = stt_result["text"]

        estimated_tokens = self.estimate_tokens(transcription)

        criteria, overall_band, summary = self._evaluate_llm(
            topic=topic,
            transcription=transcription,
        )

        return EvaluationResult(
            overall_band=overall_band,
            summary=summary,
            criteria=criteria,
            estimated_tokens_used=estimated_tokens,
        )

    def _evaluate_llm(
        self,
        topic: str,
        transcription: str,
    ) -> tuple[list[CriterionFeedback], float, str]:
        prompt = self._build_prompt(topic, transcription)
        llm_result = self.llm_model.evaluate(prompt)
        return split_output(llm_result)

    @staticmethod
    def _build_prompt(topic: str, transcription: str) -> str:
        return (
            "Role: Act as a professional IELTS Speaking Examiner.\n"
            "Input: Topic and transcription of the candidate's spoken response.\n"
            "Task: Evaluate the transcription for Grammatical Range and Accuracy "
            "and Lexical Resource.\n"
            "Output Formatting Rules (Strictly Follow):\n"
            "- DO NOT include any introductory or concluding remarks.\n"
            "- FORMAT:\n\n"
            "Grammatical Range and Accuracy:\n"
            "    Comments: [Analysis of sentence structures and error frequency]\n"
            "    Examples: [List of complex structures and specific grammatical errors]\n"
            "    Suggested Band Score: [Score]\n\n"
            "Lexical Resource:\n"
            "    Comments: [Analysis of vocabulary range, precision, "
            "and stylistic appropriateness]\n"
            "    Examples: [List of good collocations and specific errors]\n"
            "    Suggested Band Score: [Score]\n\n"
            "Overall Band Score: [Calculated Score]\n\n"
            "General Feedback:\n"
            "    Strengths: [Bullet points]\n"
            "    Areas for Improvement: [Bullet points]\n"
            "    Suggestions for Enhancement: [Bullet points]\n\n"
            f"Topic: {topic}\n"
            f"Transcription: {transcription}"
        )
