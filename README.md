# Automatic Speech Recognition API

An API for using the automatic speech recognition (ASR) service.

### Setup

The API can be deployed using the docker image published alongside the repository. The API is designed to work together
with our [ASR worker](https://github.com/TartuNLP/asr-worker) worker containers and a RabbitMQ message broker.

The following environment variables should be specified when running the container:

- `MQ_USERNAME` - RabbitMQ username
- `MQ_PASSWORD` - RabbitMQ user password
- `MQ_HOST` - RabbitMQ host
- `MQ_PORT` (optional) - RabbitMQ port (`5672` by default)
- `MQ_TIMEOUT` (optional) - Message timeout in milliseconds (`600000` by default)
- `MQ_EXCHANGE` (optional) - RabbitMQ exchange name (`speech-to-text` by default)
- `MYSQL_HOST` - MySQL hostname
- `MYSQL_PORT` (optional) - MySQL hostname (`3306` by default)
- `MYSQL_USERNAME` - MySQL username
- `MYSQL_PASSWORD` - MySQL password
- `MYSQL_DATABASE` - MySQL database name. The user specified above must already have access to this database beforehand.
  Initialization and migrations will be handled automatically by this service.
- `API_USERNAME` - username that the ASR worker component will use to authenticate itself (to download audio and return
  transcriptions)
- `API_PASSWORD` - password that the ASR worker component will use to authenticate itself
- `ENDPOINT_PATH` - the endpoint path prefix if the API is deployed on a non-root path. For example,
  if `www.example.com/speech-to-text` is used, the value should be `/speech-to-text`.
- `CONFIGURATION` (optional) - if value is `debug` logging will be more detailed, this value should not be used in
  production environments where user input should not be logged.

The container uses a volume mounted at `/app/data` to temporarily store audio files and their transcriptions.

The service is available on port `80`. The API documentation is available under the `/docs` endpoint.

The RabbitMQ connection parameters are set with environment variables. By default, the exchange name `speech-to-text`
will be used and requests will be sent to the worker using the routing key `speech-to-text.{lang}` where `{lang}`
refers to the 2-letter ISO langauge code (for example `speech-to-text.et`).
