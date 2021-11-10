import json
import logging

from aio_pika import connect_robust, ExchangeType, Message

LOGGER = logging.getLogger(__name__)


# TODO handle dead letters

class MQConnector:
    def __init__(self, host: str, port: int, username: str, password: str, exchange_name: str, message_timeout: int):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self.message_timeout = message_timeout
        self.exchange_name = exchange_name

        self.connection = None
        self.exchange = None

    async def connect(self):
        self.connection = await connect_robust(
            host=self._host,
            port=self._port,
            login=self._username,
            password=self._password
        )
        channel = await self.connection.channel()
        self.exchange = await channel.declare_exchange(self.exchange_name, ExchangeType.DIRECT)

    async def disconnect(self):
        await self.connection.close()

    async def publish_request(self, correlation_id: str, file_extension: str, language: str):
        body = json.dumps({"correlation_id": correlation_id,
                           "file_extension": file_extension}).encode()
        await self.exchange.publish(
            Message(
                body,
                correlation_id=correlation_id,
                expiration=self.message_timeout
            ),
            routing_key=f"{self.exchange_name}.{language}"
        )
        LOGGER.info(f"Sent request: {{id: {correlation_id}, routing_key: {self.exchange_name}.{language}}}")
