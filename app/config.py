from pydantic import BaseSettings


class APISettings(BaseSettings):
    username: str = 'user'
    password: str = 'pass'
    # todo datetime from str
    cleanup_interval: int = 600  # 10 minutes - run db & file cleanup
    expiration_time: int = 1200  # 20 minutes - expire / cancel jobs without updates
    remove_time: int = 86400  # 24 h - remove db records after expiration / cancellation

    storage_path: str = './data'

    class Config:
        env_prefix = 'api_'


class MQSettings(BaseSettings):
    host: str = 'localhost'
    port: int = 5672
    username: str = 'user'
    password: str = 'pass'
    exchange: str = 'speech-to-text'
    timeout: int = 600000  # 10 minutes

    class Config:
        env_prefix = 'mq_'


class DBSettings(BaseSettings):
    host: str = 'localhost'
    port: int = 3306
    username: str = 'user'
    password: str = 'pass'
    database: str = 'speech_to_text'

    class Config:
        env_prefix = 'mysql_'


api_settings = APISettings()
mq_settings = MQSettings()
db_settings = DBSettings()
