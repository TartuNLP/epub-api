import logging
import datetime
from sqlalchemy import select, update, delete, and_

from app.api import State
from app.config import api_settings
from app.database import Job, session_maker

LOGGER = logging.getLogger(__name__)


async def _read_expired(session, current_time):
    statement = select(Job.job_id).filter(and_(
        Job.updated_at < current_time - datetime.timedelta(seconds=api_settings.expiration_threshold),
        Job.state.in_([State.EXPIRED, State.ERROR])
    ))

    jobs = await session.execute(statement)
    jobs = jobs.scalars().fetchall()

    return jobs


async def _update_expired(session, current_time):
    to_cancel = and_(
        Job.updated_at < current_time - datetime.timedelta(seconds=api_settings.expiration_threshold),
        Job.state.in_([State.QUEUED, State.IN_PROGRESS])
    )
    to_expire = and_(
        Job.updated_at < current_time - datetime.timedelta(seconds=api_settings.expiration_threshold),
        Job.state == State.COMPLETED
    )

    cancel_statement = update(Job).filter(to_cancel) \
        .values(state=State.ERROR, error_message="Job timed out.")
    expire_statement = update(Job).filter(to_expire) \
        .values(state=State.EXPIRED)

    await session.execute(cancel_statement)
    await session.execute(expire_statement)
    await session.commit()


async def _delete_expired(session, current_time):
    statement = delete(Job).filter(
        and_(Job.updated_at < (current_time - datetime.timedelta(seconds=api_settings.removal_threshold)),
             Job.state.in_([State.EXPIRED, State.ERROR])))

    await session.execute(statement)
    await session.commit()


async def db_cleanup():
    current_time = datetime.datetime.utcnow()

    async with session_maker() as session:
        expired_jobs = await _read_expired(session, current_time)
        await _update_expired(session, current_time)
        await _delete_expired(session, current_time)

    return expired_jobs
