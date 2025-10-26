from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from .models import Base, NewsModel

import os
from dotenv import load_dotenv

from sqlalchemy import select

import logging

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DB_URL)
session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with session() as s:
        yield s

async def setup_database():
    async with engine.begin() as conn:
        logging.info('Setting up database')
        await conn.run_sync(Base.metadata.create_all)

async def drop_database():
    async with engine.begin() as conn:
        logging.info('Dropping up database')
        await conn.run_sync(Base.metadata.drop_all)


async def write_to_db(data, session: AsyncSession):
    for item in data:
        query = select(NewsModel).where(NewsModel.title == item['title'])
        result = await session.execute(query)

        if result.scalar_one_or_none():
            logging.info(f'News with title "{item['title']}" already in database')
            continue
        new_item = NewsModel(
            title=item['title'],
            text=item['text'],
            date=item['date'],
        )
        session.add(new_item)
    logging.info(f'News added to database')
    await session.commit()