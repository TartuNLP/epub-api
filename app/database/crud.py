import logging

import sqlalchemy.orm
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException

from app.api import State, schemas
from app.database import Job

LOGGER = logging.getLogger(__name__)


async def create_job(session: AsyncSession, job_id: str, file_name: str, language: str) -> schemas.JobInfo:
    job_info = Job(
        job_id=job_id,
        file_name=file_name,
        language=language,
        state=State.QUEUED
    )

    session.add(job_info)
    await session.commit()
    await session.refresh(job_info)
    return job_info.to_job_info()


async def _read_job(session: AsyncSession, job_id) -> Job:
    query = select(Job).filter(Job.job_id == job_id)
    LOGGER.debug(f"Querying job '{job_id}'.")
    result = await session.execute(query)
    try:
        job_info = result.scalars().one()
    except sqlalchemy.orm.exc.NoResultFound:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job_info


async def read_job(session: AsyncSession, job_id) -> schemas.Result:
    job_info = await _read_job(session, job_id)
    return job_info.to_result()


async def update_job(session: AsyncSession, job_id: str, state: State,
                     error_message: str = None) -> schemas.JobInfo:
    job_info = await _read_job(session, job_id)
    job_info.state = state
    if error_message is not None:
        job_info.error_message = error_message
    await session.commit()
    await session.refresh(job_info)
    return job_info.to_job_info()


async def delete_job():
    # Not implemented
    pass
