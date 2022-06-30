import logging
import asyncio
import os.path
from contextlib import suppress

import aiofiles.os

from app.config import api_settings
from app.database import db_cleanup

LOGGER = logging.getLogger(__name__)


async def _run():
    while True:
        await asyncio.sleep(api_settings.cleanup_interval)
        LOGGER.info("Running cleanup.")

        expired_jobs = await db_cleanup()
        LOGGER.debug(f"Removing files for: {expired_jobs}")

        for job_id in expired_jobs:
            await aiofiles.os.remove(os.path.join(api_settings.storage_path, f"{job_id}.txt"))
            await aiofiles.os.remove(os.path.join(api_settings.storage_path, f"{job_id}.wav"))

        LOGGER.info("Cleanup finished.")


class Cleanup:
    _running = False
    _task = None

    async def start(self):
        if not self._running:
            self._running = True
            self._task = asyncio.ensure_future(_run())

    async def stop(self):
        if self._running:
            self._running = False
            self._task.cancel()
            with suppress(asyncio.exceptions.CancelledError):
                await self._task


cleanup = Cleanup()
