import aiosqlite
from pathlib import Path
from contextlib import asynccontextmanager


@asynccontextmanager
async def get_db_connection(db_path: Path):
    conn = await aiosqlite.connect(
        db_path,
        timeout=30.0,
    )
    try:
        await conn.execute("PRAGMA journal_mode=WAL")
        await conn.execute("PRAGMA synchronous=NORMAL")
        await conn.execute("PRAGMA busy_timeout=30000")
        yield conn
    finally:
        await conn.close()
