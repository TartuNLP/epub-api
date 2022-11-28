from curses import meta
from email.policy import default
import os
import re
import json
from tokenize import String
import uuid
import logging

import aiofiles
import aiofiles.os
from app.api.enums import Speaker
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, Header, Response
from starlette.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app import database, api_settings
from app.api import JobInfo, State, get_username, ErrorMessage #, Result, WorkerResponse
from app.rabbitmq import publish

FILENAME_RE = re.compile(r"[\w\- ]+\.epub|blob")

LOGGER = logging.getLogger(__name__)

router = APIRouter()


def uuid4():
    """Cryptographycally secure UUID generator."""
    return uuid.UUID(bytes=os.urandom(16), version=4)


def check_uuid(job_id: str):
    try:
        uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(400, "Bad UUID provided.")


@router.post('/', response_model=JobInfo, response_model_exclude_none=True,
             description="Submit a new ebook job.", status_code=202,
             responses={400: {"model": ErrorMessage}})
async def create_job(response: Response,
                     file: UploadFile = File(..., media_type="application/epub+zip"),
                     speaker: Speaker = Form(default=Speaker.Mari),
                     speed: float = Form(default=1.0),
                     session: AsyncSession = Depends(database.get_session)):
    if file.content_type != "application/epub+zip":
        raise HTTPException(400, "Unsupported file type.")
    if speed < 0.5 or speed > 2.0:
        raise HTTPException(400, "Parameter 'speed' out of range.")

    if not FILENAME_RE.fullmatch(file.filename):
        LOGGER.debug(f"Bad filename: {file.filename}")
        raise HTTPException(400, "Filename contains unsuitable characters "
                                 "(allowed: letters, numbers, spaces, undescores) "
                                 "or does not end with '.epub'")

    job_id = str(uuid4())
    filename = file.filename

    async with aiofiles.open(os.path.join(api_settings.storage_path, f"{job_id}.epub"), 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)

    job_info = await database.create_job(session, job_id, filename, speaker, speed)
    await publish(job_id, file_extension="epub")

    response.headers['Content-Disposition'] = 'attachment; filename="api.json"'
    return job_info


@router.post('/{job_id}/rerun', response_model=JobInfo, response_model_exclude_none=True,
             description="Rerun an already present ebook job.", status_code=202,
             responses={400: {"model": ErrorMessage}})
async def create_job(response: Response,
                    job_id: str,
                    session: AsyncSession = Depends(database.get_session)):
    try:
        job_info = await database.read_job(session, job_id)
    except Exception as e:
        raise HTTPException(409, f"Job '{job_id}' is not present, cannot rerun.")
    
    await database.update_job(session, job_id, State.QUEUED)
    await publish(job_id, file_extension="epub")

    response.headers['Content-Disposition'] = 'attachment; filename="api.json"'
    return job_info


@router.get('/{job_id}', response_model=JobInfo, response_model_exclude_none=True,
            responses={404: {"model": ErrorMessage},
                       400: {"model": ErrorMessage}},
            dependencies=[Depends(check_uuid)])
async def get_job_info(job_id: str, session: AsyncSession = Depends(database.get_session)):
    return await database.read_job(session, job_id)

'''
@router.get('/{job_id}/stop', response_model=JobInfo, response_model_exclude_none=True,
            responses={404: {"model": ErrorMessage},
                       400: {"model": ErrorMessage}},
            dependencies=[Depends(check_uuid)])
async def get_job_info(job_id: str, session: AsyncSession = Depends(database.get_session)):
    job_info = await database.read_job(session, job_id)
    if job_info.state in [State.QUEUED, State.IN_PROGRESS, State.COMPLETED]:
        await database.update_job(session, job_id, State.EXPIRED)
    return await database.read_job(session, job_id)
'''

@router.get('/{job_id}/audiobook', response_class=FileResponse,
            responses={404: {"model": ErrorMessage},
                       400: {"model": ErrorMessage},
                       200: {"content": {"application/zip": {}}, "description": "Returns the original audio file."}
            },
            dependencies=[Depends(check_uuid)])
async def get_audiobook(job_id: str, session: AsyncSession = Depends(database.get_session)):
    job_info = await database.read_job(session, job_id)
    file_path = os.path.join(api_settings.storage_path, f"{job_id}.zip")
    if job_info.state == State.COMPLETED and os.path.exists(file_path):
        return FileResponse(file_path, filename=f"{job_id}.zip")


@router.get('/{job_id}/epub', response_class=FileResponse,
            responses={
                404: {"model": ErrorMessage},
                200: {"content": {"application/epub+zip": {}}, "description": "Returns the original audio file."}
            },
            dependencies=[Depends(check_uuid)])
async def get_epub(job_id: str, _: str = Depends(get_username),
                    session: AsyncSession = Depends(database.get_session)):
    job_info = await database.read_job(session, job_id)
    if job_info.state in [State.QUEUED, State.IN_PROGRESS]:
        if job_info.state == State.QUEUED:
            await database.update_job(session, job_id, State.IN_PROGRESS)
        return FileResponse(os.path.join(api_settings.storage_path, f"{job_id}.epub"), filename=f"{job_id}.epub")


@router.post('/{job_id}/failed', response_model=JobInfo, response_model_exclude_none=True,
             description="Post error message and fail job.", status_code=202,
             responses={400: {"model": ErrorMessage}},
             dependencies=[Depends(check_uuid)])
async def submit_audiobook(job_id: str,
                               error: str = Form(default="Failed to synthesize audiobook."),
                               _: str = Depends(get_username),
                               session: AsyncSession = Depends(database.get_session)):
    job_info = await database.read_job(session, job_id)
    if job_info.state == State.IN_PROGRESS:
        await database.update_job(session, job_id, State.ERROR, error_message=error)
    else:  # HTTP 409 - conflict
        raise HTTPException(409, f"Job '{job_id}' is not in progress. Current state: {job_info.state}")
    return await database.read_job(session, job_id)


@router.post('/{job_id}/audiobook', response_model=JobInfo, response_model_exclude_none=True,
             description="Post audiobook and complete job.", status_code=202,
             responses={400: {"model": ErrorMessage}},
             dependencies=[Depends(check_uuid)])
async def submit_audiobook(job_id: str,
                               file: UploadFile = File(..., media_type="application/zip"),
                               _: str = Depends(get_username),
                               session: AsyncSession = Depends(database.get_session)):
    if file.content_type != "application/zip":
        raise HTTPException(422, "Unsupported content type.")
    job_info = await database.read_job(session, job_id)
    if job_info.state == State.IN_PROGRESS:
        async with aiofiles.open(os.path.join(api_settings.storage_path, f"{job_id}.zip"), 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        await database.update_job(session, job_id, State.COMPLETED)
    else:  # HTTP 409 - conflict
        raise HTTPException(409, f"Job '{job_id}' is not in progress. Current state: {job_info.state}")
    return await database.read_job(session, job_id)
