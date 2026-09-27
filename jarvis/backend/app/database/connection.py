import aiosqlite
from typing import AsyncGenerator
from loguru import logger
from app.config import get_settings

class DatabaseManager:
    def __init__(self):
        self.settings = get_settings()
        self.db_path = self.settings.DB_PATH

    async def get_connection(self) -> aiosqlite.Connection:
        conn = await aiosqlite.connect(self.db_path)
        conn.row_factory = aiosqlite.Row
        await conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    async def initialize(self):
        from app.database.migrations import create_tables
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            await conn.execute("PRAGMA foreign_keys = ON;")
            await create_tables(conn)
            logger.info("Database initialized successfully at {}", self.db_path)

db_manager = DatabaseManager()

async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    conn = await db_manager.get_connection()
    try:
        yield conn
    finally:
        await conn.close()
