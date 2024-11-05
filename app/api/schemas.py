from doctest import Example
import imp
from pydoc import describe
from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field

#from fastapi import UploadFile, Form, File

from app.api import State, Speaker


class ErrorMessage(BaseModel):
    detail: str = Field(description="Human-readable error message.")


class JobInfo(BaseModel):
    job_id: str = Field(...,
                        description="Randomly generated job UUID.",
                        example="08d99935-6ffd-4780-870a-d6f0cc863d77")
    created_at: datetime = Field(...,
                        description="Job creation time.")
    updated_at: datetime = Field(...,
                        description="Last state change time.")
    speaker: str = Field(...,
                        description="Speaker voice to synthesize with",
                        example=Speaker.Mari)
    speed: float = Field(...,
                        description="Speed to synthesize with (in range 0.5-2.0).",
                        example=1.0)
    file_name: str = Field(...,
                        description="Original name of the uploaded file",
                        example="book.epub")
    state: str = Field(...,
                        description="Job state.",
                        example=State.QUEUED)
    error_message: Optional[str] = Field(None,
                        description="Error message for failed job.",
                        example="Parsing error.")

    class Config:
        from_attributes = True


class Result(JobInfo):
    error_message: Optional[str] = Field(None,
                                description="An optional human-readable error message.")
    audiobook: str = Field(None,
                                description="Synthesized audiobook zip file name.",
                                example="book.zip")
