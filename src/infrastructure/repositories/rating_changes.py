import aiosqlite
from datetime import datetime
from pathlib import Path
from typing import Optional

from domain.models.rating_change import RatingChange
from domain.repositories.rating_changes import RatingChangeRepository


class RatingChangeRepositoryImpl(RatingChangeRepository):
    def __init__(self, db_path: Path):
        self.db_path = db_path

    async def _init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS rating_changes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    contest_id INTEGER NOT NULL,
                    contest_name TEXT NOT NULL,
                    handle TEXT NOT NULL,
                    rank INTEGER NOT NULL,
                    rating_update_time_seconds INTEGER NOT NULL,
                    old_rating INTEGER NOT NULL,
                    new_rating INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    UNIQUE(user_id, contest_id)
                )
                """
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_rating_changes_user_id ON rating_changes(user_id)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_rating_changes_contest_id ON rating_changes(contest_id)"
            )
            await db.commit()

    async def find_by_user_and_contest(
        self, user_id: int, contest_id: int
    ) -> Optional[RatingChange]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM rating_changes WHERE user_id = ? AND contest_id = ?",
                (user_id, contest_id),
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return RatingChange(
                        id=row["id"],
                        user_id=row["user_id"],
                        contest_id=row["contest_id"],
                        contest_name=row["contest_name"],
                        handle=row["handle"],
                        rank=row["rank"],
                        rating_update_time_seconds=row["rating_update_time_seconds"],
                        old_rating=row["old_rating"],
                        new_rating=row["new_rating"],
                        created_at=datetime.fromisoformat(row["created_at"])
                        if row["created_at"]
                        else None,
                        updated_at=datetime.fromisoformat(row["updated_at"])
                        if row["updated_at"]
                        else None,
                    )
                return None

    async def create(self, rating_change: RatingChange) -> RatingChange:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """INSERT OR IGNORE INTO rating_changes
                   (user_id, contest_id, contest_name, handle, rank,
                    rating_update_time_seconds, old_rating, new_rating)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    rating_change.user_id,
                    rating_change.contest_id,
                    rating_change.contest_name,
                    rating_change.handle,
                    rating_change.rank,
                    rating_change.rating_update_time_seconds,
                    rating_change.old_rating,
                    rating_change.new_rating,
                ),
            )
            await db.commit()
            if cursor.lastrowid:
                rating_change.id = cursor.lastrowid
            return rating_change

    async def create_many(self, rating_changes: list[RatingChange]) -> None:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            for rating_change in rating_changes:
                await db.execute(
                    """INSERT OR IGNORE INTO rating_changes
                       (user_id, contest_id, contest_name, handle, rank,
                        rating_update_time_seconds, old_rating, new_rating)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        rating_change.user_id,
                        rating_change.contest_id,
                        rating_change.contest_name,
                        rating_change.handle,
                        rating_change.rank,
                        rating_change.rating_update_time_seconds,
                        rating_change.old_rating,
                        rating_change.new_rating,
                    ),
                )
            await db.commit()

    async def find_by_user_id(self, user_id: int) -> list[RatingChange]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM rating_changes WHERE user_id = ? ORDER BY rating_update_time_seconds DESC",
                (user_id,),
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    RatingChange(
                        id=row["id"],
                        user_id=row["user_id"],
                        contest_id=row["contest_id"],
                        contest_name=row["contest_name"],
                        handle=row["handle"],
                        rank=row["rank"],
                        rating_update_time_seconds=row["rating_update_time_seconds"],
                        old_rating=row["old_rating"],
                        new_rating=row["new_rating"],
                        created_at=datetime.fromisoformat(row["created_at"])
                        if row["created_at"]
                        else None,
                        updated_at=datetime.fromisoformat(row["updated_at"])
                        if row["updated_at"]
                        else None,
                    )
                    for row in rows
                ]

    async def find_latest_by_user_id(
        self, user_id: int, limit: int = 1
    ) -> list[RatingChange]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM rating_changes WHERE user_id = ? ORDER BY rating_update_time_seconds DESC LIMIT ?",
                (user_id, limit),
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    RatingChange(
                        id=row["id"],
                        user_id=row["user_id"],
                        contest_id=row["contest_id"],
                        contest_name=row["contest_name"],
                        handle=row["handle"],
                        rank=row["rank"],
                        rating_update_time_seconds=row["rating_update_time_seconds"],
                        old_rating=row["old_rating"],
                        new_rating=row["new_rating"],
                        created_at=datetime.fromisoformat(row["created_at"])
                        if row["created_at"]
                        else None,
                        updated_at=datetime.fromisoformat(row["updated_at"])
                        if row["updated_at"]
                        else None,
                    )
                    for row in rows
                ]
