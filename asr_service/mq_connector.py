import json
import logging

from aio_pika import connect, ExchangeType, Message

LOGGER = logging.getLogger("uvicorn.error")


class MQConnector:
    def __init__(self, host: str, port: int, username: str, password: str, exchange_name: str, message_timeout: int):
        """
        Initializes a RabbitMQ producer class used for publishing requests using the relevant routing key and
        receiving a response.
        """
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self.message_timeout = message_timeout
        self.exchange_name = exchange_name

        self.exchange = None

    async def connect(self):
        connection = await connect(host=self._host, port=self._port, login=self._username, password=self._password)
        channel = await connection.channel()
        self.exchange = await channel.declare_exchange(self.exchange_name, ExchangeType.DIRECT)

    async def publish_request(self, correlation_id: str, language: str):
        """
        Publishes the request to RabbitMQ, if no queue bound with the used routing key exists,
        the request is aborted with HTTP error 503 as there are no matching workers listening.
        """
        body = json.dumps({"correlation_id": correlation_id}).encode()
        await self.exchange.publish(
            Message(body, correlation_id=correlation_id, expiration=self.message_timeout),
            routing_key=f"{self.exchange_name}.{language}"
        )
