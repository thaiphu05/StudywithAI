from src.schemas.result import EvaluationResult
from src.models.LLM_model import LLMModel
from src.models.STT_model import STTModel
from src.utils.llm import split_output


class ScoringSpeakingService:
    def __init__(self):
        self.llm_model = LLMModel()
        self.stt_model = STTModel()

    @staticmethod
    def estimate_tokens(text: str) -> int:
        return max(1, len(text)) // 4

    def evaluate_fluency(self, audio: bytes, estimated_tokens: int) -> EvaluationResult: 
        pass
    
    def evaluate_grammatical_lexical(self, topic: str, transcription: str, estimated_tokens: int) -> EvaluationResult:
        prompt = (
            """Role: Act as a professional IELTS Speaking Examiner.
Input Data: User will provide the transcription of the candidate's spoken response.
Task: Evaluate the transcription in detail. You MUST cross-reference the transcription's content with the specific requirements of the IELTS Speaking criteria to accurately assess the "Grammatical Range and Accuracy" and "
Lexical Resource" scores (e.g., did the candidate use a variety of sentence structures? is the vocabulary range appropriate and precise?).
Output Formatting Rules (Strictly Follow):
DO NOT include any introductory remarks, greetings, or conversational filler.
DO NOT include any concluding remarks.
FORMAT: Use the exact structure below:
Grammatical Range and Accuracy:
    Comments: [Analysis of sentence structures and error frequency]
    Examples: [List of complex structures and specific grammatical errors]
    Suggested Band Score: [Score]   
Lexical Resource:
    Comments: [Analysis of vocabulary range, precision, and stylistic appropriateness]
    Examples: [List of good collocations and specific errors]
    Suggested Band Score: [Score]l
Overall Band Score: [Calculated Score]
General Feedback:
    Strengths: [Bullet points]
    Areas for Improvement: [Bullet points] 
    Suggestions for Enhancement: [Bullet points]""" + "\n" +"Topic" + ": " + topic + "\n" + "Transcription: " + transcription
        )
        llm_result = self.llm_model.evaluate(prompt)
        criteria, overall_band, summary = split_output(llm_result)
        return EvaluationResult(
            criteria=criteria,
            overall_band=overall_band,
            summary=summary
        )
