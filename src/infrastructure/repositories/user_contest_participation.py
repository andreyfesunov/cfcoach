import aiosqlite
from datetime import datetime
from pathlib import Path
from typing import Optional

from domain.models.user_contest_participation import UserContestParticipation
from domain.repositories.user_contest_participation import (
    UserContestParticipationRepository,
)


class UserContestParticipationRepositoryImpl(UserContestParticipationRepository):
    def __init__(self, db_path: Path):
        self.db_path = db_path

    async def _init_db(self):
        async with aiosqlite.connect(self.db_path, timeout=30.0) as db:
            await db.execute("PRAGMA journal_mode=WAL")
            await db.execute("PRAGMA busy_timeout=30000")
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS user_contest_participation (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    contest_id INTEGER NOT NULL,
                    participated INTEGER NOT NULL,
                    first_submission_time INTEGER,
                    last_submission_time INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    UNIQUE(user_id, contest_id)
                )
                """
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_participation_user_id ON user_contest_participation(user_id)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_participation_contest_id ON user_contest_participation(contest_id)"
            )
            await db.commit()

    async def find_by_user_and_contest(
        self, user_id: int, contest_id: int
    ) -> Optional[UserContestParticipation]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path, timeout=30.0) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM user_contest_participation WHERE user_id = ? AND contest_id = ?",
                (user_id, contest_id),
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return UserContestParticipation(
                        id=row["id"],
                        user_id=row["user_id"],
                        contest_id=row["contest_id"],
                        participated=bool(row["participated"]),
                        first_submission_time=row["first_submission_time"],
                        last_submission_time=row["last_submission_time"],
                        created_at=datetime.fromisoformat(row["created_at"])
                        if row["created_at"]
                        else None,
                        updated_at=datetime.fromisoformat(row["updated_at"])
                        if row["updated_at"]
                        else None,
                    )
                return None

    async def create(
        self, participation: UserContestParticipation
    ) -> UserContestParticipation:
        await self._init_db()
        async with aiosqlite.connect(self.db_path, timeout=30.0) as db:
            cursor = await db.execute(
                """INSERT OR IGNORE INTO user_contest_participation
                   (user_id, contest_id, participated, first_submission_time, last_submission_time)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    participation.user_id,
                    participation.contest_id,
                    1 if participation.participated else 0,
                    participation.first_submission_time,
                    participation.last_submission_time,
                ),
            )
            await db.commit()
            if cursor.lastrowid:
                participation.id = cursor.lastrowid
            return participation

    async def update(
        self, participation: UserContestParticipation
    ) -> UserContestParticipation:
        await self._init_db()
        async with aiosqlite.connect(self.db_path, timeout=30.0) as db:
            await db.execute(
                """UPDATE user_contest_participation
                   SET participated = ?, first_submission_time = ?,
                       last_submission_time = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (
                    1 if participation.participated else 0,
                    participation.first_submission_time,
                    participation.last_submission_time,
                    participation.id,
                ),
            )
            await db.commit()
            return participation

    async def find_by_user_id(self, user_id: int) -> list[UserContestParticipation]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path, timeout=30.0) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM user_contest_participation WHERE user_id = ?",
                (user_id,),
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    UserContestParticipation(
                        id=row["id"],
                        user_id=row["user_id"],
                        contest_id=row["contest_id"],
                        participated=bool(row["participated"]),
                        first_submission_time=row["first_submission_time"],
                        last_submission_time=row["last_submission_time"],
                        created_at=datetime.fromisoformat(row["created_at"])
                        if row["created_at"]
                        else None,
                        updated_at=datetime.fromisoformat(row["updated_at"])
                        if row["updated_at"]
                        else None,
                    )
                    for row in rows
                ]

    async def find_by_contest_id(
        self, contest_id: int
    ) -> list[UserContestParticipation]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path, timeout=30.0) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM user_contest_participation WHERE contest_id = ?",
                (contest_id,),
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    UserContestParticipation(
                        id=row["id"],
                        user_id=row["user_id"],
                        contest_id=row["contest_id"],
                        participated=bool(row["participated"]),
                        first_submission_time=row["first_submission_time"],
                        last_submission_time=row["last_submission_time"],
                        created_at=datetime.fromisoformat(row["created_at"])
                        if row["created_at"]
                        else None,
                        updated_at=datetime.fromisoformat(row["updated_at"])
                        if row["updated_at"]
                        else None,
                    )
                    for row in rows
                ]
