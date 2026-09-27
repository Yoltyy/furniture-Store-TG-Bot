import os
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'database', 'database.db')
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

async_engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(bind=async_engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


async def async_main():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)