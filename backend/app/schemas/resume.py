from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResumeResponse(BaseModel):
    id: int
    original_filename: str
    content_type: str
    file_size: int
    status: str
    uploaded_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class ResumeExtractionResponse(BaseModel):
    id: int
    original_filename: str
    status: str
    extracted_text: str
    extracted_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )