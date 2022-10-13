import typing

import asyncpg
from dotenv import load_dotenv

load_dotenv()
import os


class EasySQL:
    def __init__(self) -> None:
        self.db = None
        self.cursor = None

    async def connect(self) -> typing.Optional[asyncpg.connection.Connection]:
        self.db = await asyncpg.create_pool(
            f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        )
        return self.db

    async def execute(self, query, *args) -> typing.Optional[dict]:
        async with self.db.acquire() as conn:
            await conn.execute(query, *args)

    async def fetch(self, query, *args) -> typing.Optional[dict]:
        async with self.db.acquire() as conn:
            a = await conn.fetch(query, *args)
            return dict(a)

    async def close(self) -> None:
        await self.cursor.close()
        await self.db.close()

    async def commit(self) -> None:
        await self.db.commit()

    async def rollback(self) -> None:
        await self.db.rollback()

    async def __aenter__(self) -> "EasySQL":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()
