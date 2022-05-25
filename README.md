# Automatic Speech Recognition API

An API for using the automatic speech recognition (ASR) service. The API accepts speech recognition jobs, forwards the
requests to ASR workers via RabbitMQ and stores job info in a MySQL database.

### Setup

The API can be deployed using the docker image published alongside the repository. The API is designed to work together
with our [ASR worker](https://github.com/TartuNLP/speech-to-text-worker) containers and a RabbitMQ message
broker. The container should have the following configuration specified:

Volumes:

- `/app/data` - used to temporarily store audio files and their transcriptions Environment variables:
- Connection configuration to connect to a RabbitMQ service broker:
    - `MQ_USERNAME` - RabbitMQ username
    - `MQ_PASSWORD` - RabbitMQ user password
    - `MQ_HOST` - RabbitMQ host
    - `MQ_PORT` (optional) - RabbitMQ port (`5672` by default)
    - `MQ_TIMEOUT` (optional) - Message timeout in milliseconds (`600000` by default)
    - `MQ_EXCHANGE` (optional) - RabbitMQ exchange name (`speech-to-text` by default)
- Configuration to connect to a MySQL database:
    - `MYSQL_HOST` - MySQL hostname
    - `MYSQL_PORT` (optional) - MySQL hostname (`3306` by default)
    - `MYSQL_USERNAME` - MySQL username
    - `MYSQL_PASSWORD` - MySQL password
    - `MYSQL_DATABASE` - MySQL database name. The user specified above must already have access to this database
      beforehand. Initialization and migrations will be handled automatically by this service.
- Authentication parameters for the ASR worker:
    - `API_USERNAME` - username that the ASR worker component will use to authenticate itself (to download audio and
      return transcriptions)
    - `API_PASSWORD` - password that the ASR worker component will use to authenticate itself
- Cleanup configuration for files and database records:
    - `API_CLEANUP_INTERVAL` (optional) - how often cleanup is initiated (in seconds, `600` by default)
    - `API_EXPIRATION_THRESHOLD` (optional) - number of seconds after which the job is marked as cancelled (if the job
      was still in progress) or expired (if the job was done) in the database and its files are deleted (`1200` by
      default)
    - `API_REMOVAL_THRESHOLD` (optional) - number of seconds after expiration when the database record for the job is
      deleted (`86400` by default)

The entrypoint of the container first runs the database migration and then starts the server
with `uvicorn app:app --host 0.0.0.0 --proxy-headers --log-config logging/logging.ini`. The
`CMD` parameter can be used to define additional [Uvicorn parameters](https://www.uvicorn.org/deployment/). For
example, `["--log-config", "logging/debug.ini", "--root-path", "/api/speech-to-text"]`
enables debug logging (as the last `--log-config` flag is used) and allows the API to be deployed to the non-root
path `/api/speech-to-text`.

The service is available on port `8000`. The API documentation is available under the `/docs` endpoint.

The RabbitMQ connection parameters are set with environment variables. By default, the exchange name `speech-to-text`
will be used and requests will be sent to the worker using the routing key `speech-to-text.{lang}` where `{lang}`
refers to the 2-letter ISO langauge code (for example `speech-to-text.et`).
