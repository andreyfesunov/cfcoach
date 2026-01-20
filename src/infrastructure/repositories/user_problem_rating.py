import aiosqlite
from datetime import datetime
from pathlib import Path
from typing import Optional

from domain.models.user_problem_rating import UserProblemRating
from domain.repositories.user_problem_rating import UserProblemRatingRepository


class UserProblemRatingRepositoryImpl(UserProblemRatingRepository):
    def __init__(self, db_path: Path):
        self.db_path = db_path

    async def _init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS user_problem_rating (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    contest_id INTEGER,
                    problem_index TEXT,
                    difficulty_rating INTEGER,
                    usefulness_rating INTEGER,
                    interest_rating INTEGER,
                    quality_rating INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    UNIQUE(user_id, contest_id, problem_index)
                )
                """
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_rating_user_id ON user_problem_rating(user_id)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_rating_problem ON user_problem_rating(contest_id, problem_index)"
            )
            await db.commit()

    async def find_by_user_and_problem(
        self, user_id: int, contest_id: Optional[int], problem_index: Optional[str]
    ) -> Optional[UserProblemRating]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM user_problem_rating WHERE user_id = ? AND contest_id = ? AND problem_index = ?",
                (user_id, contest_id, problem_index),
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return UserProblemRating(
                        id=row["id"],
                        user_id=row["user_id"],
                        contest_id=row["contest_id"],
                        problem_index=row["problem_index"],
                        difficulty_rating=row["difficulty_rating"],
                        usefulness_rating=row["usefulness_rating"],
                        interest_rating=row["interest_rating"],
                        quality_rating=row["quality_rating"],
                        created_at=datetime.fromisoformat(row["created_at"])
                        if row["created_at"]
                        else None,
                        updated_at=datetime.fromisoformat(row["updated_at"])
                        if row["updated_at"]
                        else None,
                    )
                return None

    async def create(self, rating: UserProblemRating) -> UserProblemRating:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """INSERT OR IGNORE INTO user_problem_rating
                   (user_id, contest_id, problem_index, difficulty_rating,
                    usefulness_rating, interest_rating, quality_rating)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    rating.user_id,
                    rating.contest_id,
                    rating.problem_index,
                    rating.difficulty_rating,
                    rating.usefulness_rating,
                    rating.interest_rating,
                    rating.quality_rating,
                ),
            )
            await db.commit()
            if cursor.lastrowid:
                rating.id = cursor.lastrowid
            return rating

    async def update(self, rating: UserProblemRating) -> UserProblemRating:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """UPDATE user_problem_rating
                   SET difficulty_rating = ?, usefulness_rating = ?,
                       interest_rating = ?, quality_rating = ?,
                       updated_at = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (
                    rating.difficulty_rating,
                    rating.usefulness_rating,
                    rating.interest_rating,
                    rating.quality_rating,
                    rating.id,
                ),
            )
            await db.commit()
            return rating

    async def find_by_user_id(self, user_id: int) -> list[UserProblemRating]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM user_problem_rating WHERE user_id = ?",
                (user_id,),
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    UserProblemRating(
                        id=row["id"],
                        user_id=row["user_id"],
                        contest_id=row["contest_id"],
                        problem_index=row["problem_index"],
                        difficulty_rating=row["difficulty_rating"],
                        usefulness_rating=row["usefulness_rating"],
                        interest_rating=row["interest_rating"],
                        quality_rating=row["quality_rating"],
                        created_at=datetime.fromisoformat(row["created_at"])
                        if row["created_at"]
                        else None,
                        updated_at=datetime.fromisoformat(row["updated_at"])
                        if row["updated_at"]
                        else None,
                    )
                    for row in rows
                ]

    async def find_by_problem(
        self, contest_id: Optional[int], problem_index: Optional[str]
    ) -> list[UserProblemRating]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM user_problem_rating WHERE contest_id = ? AND problem_index = ?",
                (contest_id, problem_index),
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    UserProblemRating(
                        id=row["id"],
                        user_id=row["user_id"],
                        contest_id=row["contest_id"],
                        problem_index=row["problem_index"],
                        difficulty_rating=row["difficulty_rating"],
                        usefulness_rating=row["usefulness_rating"],
                        interest_rating=row["interest_rating"],
                        quality_rating=row["quality_rating"],
                        created_at=datetime.fromisoformat(row["created_at"])
                        if row["created_at"]
                        else None,
                        updated_at=datetime.fromisoformat(row["updated_at"])
                        if row["updated_at"]
                        else None,
                    )
                    for row in rows
                ]
