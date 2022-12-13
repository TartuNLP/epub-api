from ipaddress import ip_address
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app import api_settings
from app.rabbitmq import mq_session
from app.database import db_engine
from app.api import router
from app.cleanup import cleanup

app = FastAPI(
    title="epub-api",
    version=api_settings.version if api_settings.version else "dev",
    description=f'A service that performs text-to-speech on uploaded epub audio book.\n\n\
        A job without updates expires after {int(api_settings.expiration_threshold/(60*60*24))} days.\n\
        Job is removed after being expired for {int(api_settings.removal_threshold/(60*60*24))} days.'
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


@app.get('/health/readiness', include_in_schema=False)
@app.get('/health/startup', include_in_schema=False)
@app.get('/health/liveness', include_in_schema=False)
async def health_check():
    # Returns 200 the connection to RabbitMQ and DB connection is up
    if mq_session.channel is None or mq_session.channel.is_closed:
        raise HTTPException(500)
    try:
        conn = await db_engine.connect()
        await conn.close()
    except Exception as e:
        print(e)
        raise HTTPException(500)

    return "OK"


class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("/health") == -1


# Filter out /endpoint
logging.getLogger("uvicorn.access").addFilter(EndpointFilter())

app.include_router(router)
