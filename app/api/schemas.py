from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field

from app.api import Language, State


class Job(BaseModel):
    job_id: str = Field(...,
                        description="Randomly generated job UUID.",
                        example="08d99935-6ffd-4780-870a-d6f0cc863d77")
    created_at: datetime = Field(...,
                                 description="Job creation time.")
    updated_at: datetime = Field(...,
                                 description="Last state change time.")
    language: Language = Field(Language.ESTONIAN,
                               description="Input language ISO 2-letter code.")
    file_name: str = Field(...,
                           description="Original name of the uploaded file",
                           example="audio.wav")
    state: str = Field(...,
                       description="Job state.",
                       example=State.QUEUED)
    error_message: Optional[str] = Field(None,
                                         description="An optional human-readable error message.",
                                         example="Unexpected file type.")
    transcription: str = Field(None,
                               description="Transcribed text.",
                               example="Tere!")

    class Config:
        orm_mode = True


class Result(BaseModel):
    result: str = Field(...,
                        description="Transcribed text segment or an error message in case ASR was not successful. "
                                    "In case the transcription is sent in multiple parts, "
                                    "only new segments should be sent.",
                        example="Tere!")
    success: bool = Field(True, description="Boolean value to show whether ASR was successful")
    final: bool = Field(True, description="Value to show whether the final part was sent.")
