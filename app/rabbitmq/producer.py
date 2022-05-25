import json
import logging

from aio_pika import Message

from app import mq_settings
from app.rabbitmq import mq_session

LOGGER = logging.getLogger(__name__)


async def publish(correlation_id: str, file_extension: str, language: str):
    body = json.dumps({"correlation_id": correlation_id,
                       "file_extension": file_extension}).encode()
    message = Message(
        body,
        content_type='application/json',
        correlation_id=correlation_id,
        expiration=mq_settings.timeout
    )

    try:
        await mq_session.exchange.publish(message, routing_key=f"{mq_settings.exchange}.{language}")
    except Exception as e:
        LOGGER.exception(e)
        LOGGER.info("Attempting to restore the channel.")
        await mq_session.channel.reopen()
        await mq_session.exchange.publish(message, routing_key=f"{mq_settings.exchange}.{language}")
    LOGGER.info(f"Sent request: {{id: {correlation_id}, routing_key: {mq_settings.exchange}.{language}}}")
