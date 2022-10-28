from pydantic import BaseSettings


class APISettings(BaseSettings):
    version: str = '2.1.0'
    username: str = 'guest'
    password: str = 'guest'
    cleanup_interval: int = 600  # 10 minutes - run db & file cleanup
    expiration_threshold: int = 6000  # 100 minutes - expire / cancel jobs without updates
    removal_threshold: int = 86400  # 24 h - remove db records after expiration / cancellation

    storage_path: str = './data'

    class Config:
        env_prefix = 'api_'


class MQSettings(BaseSettings):
    host: str = 'localhost'
    port: int = 5672
    username: str = 'guest'
    password: str = 'guest'
    exchange: str = 'epub_to_audiobook'
    timeout: int = 1200  # 20 minutes

    class Config:
        env_prefix = 'mq_'


class DBSettings(BaseSettings):
    host: str = 'localhost'
    port: int = 3306
    username: str = 'guest'
    password: str = 'guest'
    database: str = 'epub_to_audiobook'

    class Config:
        env_prefix = 'mysql_'


api_settings = APISettings()
mq_settings = MQSettings()
db_settings = DBSettings()
