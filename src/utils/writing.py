from src.schemas.result import CriterionFeedback, EvaluationResult


_CRITERIA_ORDER = [
    "Task Achievement",
    "Coherence and Cohesion",
    "Lexical Resource",
    "Grammatical Range and Accuracy",
]


def format_writing_model_output(
    predicted_scaled,
    estimated_tokens: int,
    summary: str = "",
) -> EvaluationResult:
    """Convert model output array to EvaluationResult."""
    if predicted_scaled is None or len(predicted_scaled) == 0:
        raise ValueError("Empty model output")

    row = predicted_scaled[0]
    if len(row) < 5:
        raise ValueError("Model output has insufficient dimensions")

    criteria = [
        CriterionFeedback(criterion=_CRITERIA_ORDER[0], band=float(row[0]), explanation=""),
        CriterionFeedback(criterion=_CRITERIA_ORDER[1], band=float(row[1]), explanation=""),
        CriterionFeedback(criterion=_CRITERIA_ORDER[2], band=float(row[2]), explanation=""),
        CriterionFeedback(criterion=_CRITERIA_ORDER[3], band=float(row[3]), explanation=""),
    ]

    return EvaluationResult(
        overall_band=float(row[4]),
        summary=summary,
        criteria=criteria,
        estimated_tokens_used=estimated_tokens,
    )
