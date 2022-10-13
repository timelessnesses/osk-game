from dotenv import load_dotenv

load_dotenv()
import os
import typing

import asyncpg

db: typing.Optional[asyncpg.Connection] = None


async def connect():
    dsn = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    global db
    db = await asyncpg.create_pool(dsn)
