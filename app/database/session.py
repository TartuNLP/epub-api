from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app import db_settings

db_engine = create_async_engine(f'mysql+aiomysql://'
                                f'{db_settings.username}:{db_settings.password}@'
                                f'{db_settings.host}:{db_settings.port}/'
                                f'{db_settings.database}')
session_maker = sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)


async def get_session():
    async with session_maker() as session:
        yield session
