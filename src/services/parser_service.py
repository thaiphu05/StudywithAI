from io import BytesIO

from docx import Document


class ParserService:
    @staticmethod
    def parse_docx(raw: bytes) -> str:
        document = Document(BytesIO(raw))
        return "\n".join(paragraph.text for paragraph in document.paragraphs).strip()
