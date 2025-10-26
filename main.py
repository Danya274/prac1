import logging
import asyncio
import uvicorn

from fastapi import FastAPI
from contextlib import asynccontextmanager

from app import router

from parser import parser

from database.db import setup_database, write_to_db, session



async def run_parser():
    while True:
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, parser)
            if data:
                async with session() as s:
                    await write_to_db(data, s)
            else:
                logging.info('No data')
        except Exception as e:
            logging.info(f'Error in parser loop: {e}')
        logging.info(f'Parsing complete. Next parsing in 1 hour')
        await asyncio.sleep(3600)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info('Running startup event')
    await setup_database()
    task = asyncio.create_task(run_parser())
    logging.info('Startup event finished')
    yield
    await task


app = FastAPI(lifespan=lifespan)
app.include_router(router)

if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.INFO)
        uvicorn.run('main:app', host='0.0.0.0', reload=False)
    except Exception as e:
        logging.info(f'Error: {e}')
    except KeyboardInterrupt:
        logging.info(f'Programm stopped')
