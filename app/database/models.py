from email.policy import default
from sqlalchemy import Column, String, Float, DateTime, Enum
from sqlalchemy.sql import func, text

from app.database import Base
from app.api import State, schemas


class Job(Base):
    __tablename__ = "job"
    job_id = Column(String(64), primary_key=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False,
                        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    file_name = Column(String(255), nullable=False)
    speaker = Column(String(255), default="mari", nullable=False)
    speed = Column(Float(), default=1.0, nullable=False)
    state = Column(Enum(State), nullable=False)
    error_message = Column(String(255), default=None, nullable=True)

    def to_job_info(self):
        return schemas.JobInfo.from_orm(self)

    def to_result(self):
        return schemas.Result.from_orm(self)
