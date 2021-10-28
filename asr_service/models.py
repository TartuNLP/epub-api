from typing import Optional
from enum import Enum
from datetime import datetime

from pydantic import BaseModel, Field


class Language(str, Enum):
    estonian = "et"


class State(str, Enum):
    created = "created"
    in_progress = "in progress"
    completed = "completed"
    done = "done"
    error = "error"


class JobInfo(BaseModel):
    job_id: str = Field(...,
                        description="Randomly generated job UUID.",
                        example="08d99935-6ffd-4780-870a-d6f0cc863d77")
    created_at: datetime = Field(...,
                                 description="Job creation time.")
    state_changed: str = Field(...,
                               description="Last state change time.")
    language: Language = Field(Language.estonian,
                               description="Input language ISO 2-letter code.")
    file_name: str = Field(...,
                           description="Original name of the uploaded file",
                           example="audio.wav")
    state: str = Field(...,
                       description="Job state.",
                       example=State.created)
    error_message: Optional[str] = Field(None,
                                         description="An optional human-readable error message.",
                                         example="Unexpected file type.")


class TranscriptionWorkerOutput(BaseModel):
    result: str = Field(..., description="Transcribed text or an error message in case ASR was not successful.",
                        example="Tere!")
    success: bool = Field(True, description="Boolean value to show whether ASR was successful")


class TranscriptionResult(BaseModel):
    transcription: str = Field(...,
                               description="Transcribed text.",
                               example="Tere!")
    #job_info: JobInfo TODO
