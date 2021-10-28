from os import environ
from pika import ConnectionParameters, credentials

EXCHANGE = 'speech-to-text'

MQ_PARAMETERS = ConnectionParameters(
    host=environ.get('MQ_HOST', 'localhost'),
    port=int(environ.get('MQ_PORT', '5672')),
    credentials=credentials.PlainCredentials(
        username=environ.get('MQ_USERNAME', 'guest'),
        password=environ.get('MQ_PASSWORD', 'guest')
    )
)

DATA_PATH = environ.get('DATA_PATH', '/app/data')

ASR_USERNAME = environ.get('ASR_USERNAME', 'user')
ASR_PASSWORD = environ.get('ASR_PASSWORD', 'pass')

DB_CONNECTION_STRING = environ.get('DB_CONNECTION_STRING')