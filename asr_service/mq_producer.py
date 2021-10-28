import json
import uuid
import logging
from sys import getsizeof

from typing import Dict

from flask import abort
import pika
import pika.exceptions


LOGGER = logging.getLogger("gunicorn.error")


class MQProducer:
    def __init__(self, connection_parameters: pika.connection.Parameters, exchange_name: str):
        """
        Initializes a RabbitMQ producer class used for publishing requests using the relevant routing key and
        receiving a response.
        """
        self.response = None
        self.correlation_id = None
        self.exchange_name = exchange_name

        try:
            self.mq_connection = pika.BlockingConnection(connection_parameters)
            self.channel = self.mq_connection.channel()
        except Exception as e:
            LOGGER.error(e)
            abort(503)

    def publish_request(self, content: Dict, message_timeout: int) -> dict:
        """
        Publishes the request to RabbitMQ, if no queue bound with the used routing key exists,
        the request is aborted with HTTP error 503 as there are no matching workers listening.
        """
        self.channel.confirm_delivery()
        self.correlation_id = str(uuid.uuid4())
        body = json.dumps(content).encode()
        try:
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=self.exchange_name,
                properties=pika.BasicProperties(
                    correlation_id=self.correlation_id,
                    expiration=str(message_timeout)),
                mandatory=True,
                body=body
            )
            LOGGER.debug(f"Sent request: {{id: {self.correlation_id}}}")

            self.channel.close()
            self.mq_connection.close()
            return {"correlation_id": self.correlation_id} # TODO

        except pika.exceptions.UnroutableError:
            self.channel.close()
            self.mq_connection.close()
            return {'status': "Request cannot be processed. Check your request or try again later.",
                    'status_code': 503}
