from pydantic import BaseModel


class UploadResponse(BaseModel):
    message: str
    filename: str
    content_type: str
