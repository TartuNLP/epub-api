from os import environ

EXCHANGE = 'speech-to-text'

MQ_HOST=environ.get('MQ_HOST', 'localhost')
MQ_PORT=int(environ.get('MQ_PORT', '5672'))
MQ_USERNAME=environ.get('MQ_USERNAME', 'guest')
MQ_PASSWORD=environ.get('MQ_PASSWORD', 'guest')

MQ_TIMEOUT = int(environ.get('MESSAGE_TIMEOUT', 60000)) # 10 min

DATA_PATH = environ.get('DATA_PATH', './data')

ASR_USERNAME = environ.get('ASR_USERNAME', 'user')
ASR_PASSWORD = environ.get('ASR_PASSWORD', 'pass')

DB_CONNECTION_STRING = environ.get('DB_CONNECTION_STRING')