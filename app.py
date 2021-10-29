import logging
import os
import uuid
from datetime import datetime

import aiofiles as aiofiles
from fastapi import FastAPI, Depends, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse

from asr_service.models import TranscriptionWorkerOutput, JobInfo, State, TranscriptionResult, Language
from asr_service.mq_connector import MQConnector
from asr_service.auth import Auth
from asr_service import settings

logger = logging.getLogger("uvicorn.error")

app = FastAPI(
    title="ASR Service",
    version="0.1.0",
    description="A service that performs automatic speech recognition (ASR) on uploaded audio files."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

auth = Auth(settings.ASR_USERNAME, settings.ASR_PASSWORD)

mq_connector = MQConnector(host=settings.MQ_HOST,
                           port=settings.MQ_PORT,
                           username=settings.MQ_USERNAME,
                           password=settings.MQ_PASSWORD,
                           exchange_name=settings.EXCHANGE,
                           message_timeout=settings.MQ_TIMEOUT)

db_connector = None  # TODO


@app.on_event("startup")
async def mq_connect():
    await mq_connector.connect()
    # await db_connector.connect() TODO


# TODO content limit
@app.post('/', response_model=JobInfo, description="Submit a new ASR job.")
async def new_job(file: UploadFile = File(..., media_type="audio/wav"),
                  language: str = Form(default=Language.estonian, description="Input language ISO 2-letter code.")):
    job_id = str(uuid.uuid4())
    filename = file.filename
    created = str(datetime.now())

    async with aiofiles.open(os.path.join(settings.DATA_PATH, f"{job_id}.wav"), 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)

    # TODO Job info to DB
    # TODO Post job info to RabbitMQ
    await mq_connector.publish_request(job_id, language)

    return JobInfo(
        job_id=job_id,
        file_name=filename,
        created_at=created,
        state_changed=created,
        state=State.created,
        language=language
    )


@app.get('/{job_id}/status', response_model=JobInfo)
def get_status(job_id: str):
    pass  # TODO return job state from DB


@app.get('/{job_id}/audio', response_class=FileResponse,
         responses={200: {"content": {"audio/wav": {}}, "description": "Returns the original audio file."}})
async def get_audio(job_id: str, _: str = Depends(auth.get_username)):
    # TODO check job state from DB (created or in progress) and set to in progress
    return FileResponse(os.path.join(settings.DATA_PATH, f"{job_id}.wav"))


@app.get('/{job_id}/transcription', response_model=TranscriptionResult)
async def get_transcription(job_id: str):
    # TODO check that job exists and is in status "completed"
    async with aiofiles.open(os.path.join(settings.DATA_PATH, f"{job_id}.txt"), 'r') as file:
        content = await file.read()
    # TODO set to "done"
    return TranscriptionResult(
        transcription=content,
        # job_info = None # TODO
    )


@app.post('/{job_id}/transcription', response_model=JobInfo)
async def submit_transcription(job_id: str, worker_output: TranscriptionWorkerOutput,
                               _: str = Depends(auth.get_username)):
    # TODO check that job exists and is in status "in progress"
    if worker_output.success:
        async with aiofiles.open(os.path.join(settings.DATA_PATH, f"{job_id}.txt"), 'w') as out_file:
            await out_file.write(worker_output.result)
        # TODO set to "completed"
    else:
        pass  # TODO set to "error"
