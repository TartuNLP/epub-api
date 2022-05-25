import os
import re
import uuid

import aiofiles
import aiofiles.os
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, Header
from starlette.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app import database, api_settings
from app.api import JobInfo, Result, WorkerResponse, Language, State, get_username, ErrorMessage
from app.rabbitmq import publish

FILENAME_RE = re.compile(r"[\w\- ]+\.wav")

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
             description="Submit a new ASR job.", status_code=202,
             responses={400: {"model": ErrorMessage}})
async def create_job(file: UploadFile = File(..., media_type="audio/wav"),
                     language: Language = Form(default=Language.ESTONIAN,
                                               description="Input language ISO 2-letter code."),
                     session: AsyncSession = Depends(database.get_session)):
    if file.content_type != "audio/wav":
        raise HTTPException(400, "Unsupported file type")

    if not FILENAME_RE.fullmatch(file.filename):
        raise HTTPException(400, "Filename contains unsuitable characters "
                                 "(allowed: letters, numbers, spaces, undescores) "
                                 "or does not end with '.wav'")

    job_id = str(uuid4())
    filename = file.filename

    async with aiofiles.open(os.path.join(api_settings.storage_path, f"{job_id}.wav"), 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)

    async with aiofiles.open(os.path.join(api_settings.storage_path, f"{job_id}.txt"), 'w') as out_file:
        await out_file.write('')

    job_info = await database.create_job(session, job_id, filename, language)
    await publish(job_id, file_extension="wav", language=language)

    return job_info


@router.get('/{job_id}', response_model=Result, response_model_exclude_none=True,
            responses={404: {"model": ErrorMessage},
                       400: {"model": ErrorMessage}},
            dependencies=[Depends(check_uuid)])
async def get_job_info(job_id: str, session: AsyncSession = Depends(database.get_session)):
    job_info = await database.read_job(session, job_id)
    if job_info.state in [State.IN_PROGRESS, State.COMPLETED]:
        async with aiofiles.open(os.path.join(api_settings.storage_path, f"{job_id}.txt"), 'r') as file:
            content = await file.read()
        job_info.transcription = content.strip()
    return job_info


@router.get('/{job_id}/audio', response_class=FileResponse,
            responses={
                404: {"model": ErrorMessage},
                200: {"content": {"audio/wav": {}}, "description": "Returns the original audio file."}
            },
            dependencies=[Depends(check_uuid)])
async def get_audio(job_id: str, _: str = Depends(get_username),
                    session: AsyncSession = Depends(database.get_session)):
    job_info = await database.read_job(session, job_id)
    if job_info.state in [State.QUEUED, State.IN_PROGRESS]:
        await database.update_job(session, job_id, State.IN_PROGRESS)
        return FileResponse(os.path.join(api_settings.storage_path, f"{job_id}.wav"))


@router.post('/{job_id}/transcription',
             responses={404: {"model": ErrorMessage},
                        409: {"model": ErrorMessage},
                        422: {"model": ErrorMessage}},
             dependencies=[Depends(check_uuid)])
async def submit_transcription(job_id: str,
                               result: WorkerResponse,
                               content_type: str = Header(...),
                               _: str = Depends(get_username),
                               session: AsyncSession = Depends(database.get_session)):
    if content_type != "application/json":
        raise HTTPException(422, "Unsupported content type.")

    job_info = await database.read_job(session, job_id)
    if job_info.state == State.IN_PROGRESS:
        if result.success:
            async with aiofiles.open(os.path.join(api_settings.storage_path, f"{job_id}.txt"), 'a') as out_file:
                await out_file.write(result.result)
            if result.final:
                await database.update_job(session, job_id, State.COMPLETED)
            else:  # update timestamp only
                await database.update_job(session, job_id, State.IN_PROGRESS)
        else:
            await database.update_job(session, job_id, State.ERROR, result.result)
    else:  # HTTP 409 - conflict
        raise HTTPException(409, f"Job '{job_id}' is not in progress. Current state: {job_info.state}")
