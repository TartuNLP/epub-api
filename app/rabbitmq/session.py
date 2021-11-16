from aio_pika import connect_robust, ExchangeType

from app import mq_settings


class Session:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange = None

    async def connect(self):
        self.connection = await connect_robust(
            host=mq_settings.host,
            port=mq_settings.port,
            login=mq_settings.username,
            password=mq_settings.password
        )
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.declare_exchange(mq_settings.exchange, ExchangeType.DIRECT)

    async def disconnect(self):
        await self.connection.close()


mq_session = Session()
