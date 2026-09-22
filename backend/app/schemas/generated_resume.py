from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GeneratedResumeResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    user_id: int
    draft_id: int
    file_name: str
    file_path: str
    created_at: datetime