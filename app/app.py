from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.rabbitmq import mq_session
from app.database import db_engine
from app.api import router
from app.cleanup import cleanup

app = FastAPI(
    title="ASR Service",
    version="1.0.1",
    description="A service that performs automatic speech recognition (ASR) on uploaded audio files."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.middleware("http")
async def add_cache_control_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    return response


@app.on_event("startup")
async def startup():
    await mq_session.connect()
    await cleanup.start()


@app.on_event("shutdown")
async def shutdown():
    await cleanup.stop()
    await mq_session.disconnect()
    await db_engine.dispose()


app.include_router(router)
