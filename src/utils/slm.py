
import re

from src.schemas.result import CriterionFeedback


_CRITERIA_ALIASES: list[tuple[str, list[str]]] = [
    ("Task Response", ["Task Response", "Task Achievement"]),
    ("Coherence and Cohesion", ["Coherence and Cohesion"]),
    ("Lexical Resource", ["Lexical Resource"]),
    (
        "Grammatical Range and Accuracy",
        ["Grammatical Range and Accuracy", "Grammar Range and Accuracy"],
    ),
]


def _to_band(value: str | None) -> float:
    if not value:
        return 0.0
    try:
        band = float(value)
    except ValueError:
        return 0.0
    return max(0.0, min(9.0, band))


def _extract_band(text: str) -> float:
    # Accept common patterns: "Band 6.5", "Band Score: 7", "Score = 6".
    band_match = re.search(
        r"(?:band(?:\s*score)?|score)\s*[:=-]?\s*([0-9](?:\.[0-9])?)",
        text,
        flags=re.IGNORECASE,
    )
    if band_match:
        return _to_band(band_match.group(1))

    fallback_number = re.search(r"\b([0-9](?:\.[0-9])?)\b", text)
    return _to_band(fallback_number.group(1) if fallback_number else None)


def _clean_explanation(text: str) -> str:
    cleaned = re.sub(
        r"(?:band(?:\s*score)?|score)\s*[:=-]?\s*[0-9](?:\.[0-9])?",
        "",
        text,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip(" -:\n\t")


def split_criteria(text: str) -> list[CriterionFeedback]:
    headings = [alias for _, aliases in _CRITERIA_ALIASES for alias in aliases]
    heading_pattern = "|".join(re.escape(h) for h in headings)

    criteria: list[CriterionFeedback] = []
    for canonical_name, aliases in _CRITERIA_ALIASES:
        alias_pattern = "|".join(re.escape(a) for a in aliases)
        section_match = re.search(
            rf"(?:^|\n)\s*(?:{alias_pattern})\s*[:\-]?\s*(.*?)"
            rf"(?=(?:\n\s*(?:{heading_pattern})\s*[:\-]?)|\n\s*Overall\s+Band|\n\s*Strengths|\n\s*Areas\s+for\s+Improvement|\n\s*Suggestions\s+for\s+Enhancement|\Z)",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )

        body = section_match.group(1).strip() if section_match else ""
        criteria.append(
            CriterionFeedback(
                criterion=canonical_name,
                band=_extract_band(body),
                explanation=_clean_explanation(body),
            )
        )

    return criteria


def split_output(text: str) -> tuple[list[CriterionFeedback], float, str]:
    criteria = split_criteria(text)

    overall_match = re.search(
        r"overall\s*band(?:\s*score)?\s*[:=-]?\s*([0-9](?:\.[0-9])?)",
        text,
        flags=re.IGNORECASE,
    )
    overall_band = _to_band(overall_match.group(1) if overall_match else None)

    summary_sections: list[str] = []
    for title in ["Strengths", "Areas for Improvement", "Suggestions for Enhancement"]:
        section_match = re.search(
            rf"(?:^|\n)\s*{re.escape(title)}\s*[:\-]?\s*(.*?)"
            r"(?=(?:\n\s*(?:Strengths|Areas\s+for\s+Improvement|Suggestions\s+for\s+Enhancement)\s*[:\-]?)|\Z)",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if section_match:
            content = section_match.group(1).strip()
            if content:
                summary_sections.append(f"{title}: {content}")

    summary = "\n\n".join(summary_sections).strip()
    if not summary:
        summary = text.strip()[:500]

    return criteria, overall_band, summary