import aiosqlite
from datetime import datetime
from pathlib import Path

from domain.models.user import User
from domain.repositories.users import UserRepository


class UserRepositoryImpl(UserRepository):
    def __init__(self, db_path: Path):
        self.db_path = db_path

    async def _init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    external_id TEXT UNIQUE,
                    username TEXT,
                    access_token TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)"
            )
            await db.commit()

    async def find_by_external_id(self, external_id: str) -> User | None:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users WHERE external_id = ?", (external_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return User(
                        id=row["id"],
                        external_id=row["external_id"],
                        username=row["username"],
                        access_token=row["access_token"],
                        created_at=datetime.fromisoformat(row["created_at"])
                        if row["created_at"]
                        else None,
                        updated_at=datetime.fromisoformat(row["updated_at"])
                        if row["updated_at"]
                        else None,
                    )
                return None

    async def find_by_username(self, username: str) -> User | None:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return User(
                        id=row["id"],
                        external_id=row["external_id"],
                        username=row["username"],
                        access_token=row["access_token"],
                        created_at=datetime.fromisoformat(row["created_at"])
                        if row["created_at"]
                        else None,
                        updated_at=datetime.fromisoformat(row["updated_at"])
                        if row["updated_at"]
                        else None,
                    )
                return None

    async def create(self, user: User) -> User:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """INSERT INTO users (external_id, username, access_token)
                   VALUES (?, ?, ?)""",
                (user.external_id, user.username, user.access_token),
            )
            await db.commit()
            user.id = cursor.lastrowid
            return user

    async def update(self, user: User) -> User:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """UPDATE users
                   SET username = ?, access_token = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (user.username, user.access_token, user.id),
            )
            await db.commit()
            return user

    async def find_by_id(self, user_id: int) -> User | None:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return User(
                        id=row["id"],
                        external_id=row["external_id"],
                        username=row["username"],
                        access_token=row["access_token"],
                        created_at=datetime.fromisoformat(row["created_at"])
                        if row["created_at"]
                        else None,
                        updated_at=datetime.fromisoformat(row["updated_at"])
                        if row["updated_at"]
                        else None,
                    )
                return None

    async def find_all(self) -> list[User]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM users") as cursor:
                rows = await cursor.fetchall()
                return [
                    User(
                        id=row["id"],
                        external_id=row["external_id"],
                        username=row["username"],
                        access_token=row["access_token"],
                        created_at=datetime.fromisoformat(row["created_at"])
                        if row["created_at"]
                        else None,
                        updated_at=datetime.fromisoformat(row["updated_at"])
                        if row["updated_at"]
                        else None,
                    )
                    for row in rows
                ]
