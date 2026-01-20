import aiosqlite
from datetime import datetime
from pathlib import Path
from typing import Optional

from domain.models.submission import Submission
from domain.repositories.submissions import SubmissionRepository


class SubmissionRepositoryImpl(SubmissionRepository):
    def __init__(self, db_path: Path):
        self.db_path = db_path

    async def _init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    submission_id INTEGER UNIQUE NOT NULL,
                    contest_id INTEGER,
                    problem_index TEXT,
                    problem_name TEXT,
                    verdict TEXT NOT NULL,
                    programming_language TEXT NOT NULL,
                    creation_time_seconds INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
                """
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_submissions_user_id ON submissions(user_id)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_submissions_submission_id ON submissions(submission_id)"
            )
            await db.commit()

    async def find_by_submission_id(self, submission_id: int) -> Optional[Submission]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM submissions WHERE submission_id = ?", (submission_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return Submission(
                        id=row["id"],
                        user_id=row["user_id"],
                        submission_id=row["submission_id"],
                        contest_id=row["contest_id"],
                        problem_index=row["problem_index"],
                        problem_name=row["problem_name"],
                        verdict=row["verdict"],
                        programming_language=row["programming_language"],
                        creation_time_seconds=row["creation_time_seconds"],
                        created_at=datetime.fromisoformat(row["created_at"])
                        if row["created_at"]
                        else None,
                        updated_at=datetime.fromisoformat(row["updated_at"])
                        if row["updated_at"]
                        else None,
                    )
                return None

    async def create(self, submission: Submission) -> Submission:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """INSERT INTO submissions
                   (user_id, submission_id, contest_id, problem_index, problem_name,
                    verdict, programming_language, creation_time_seconds)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    submission.user_id,
                    submission.submission_id,
                    submission.contest_id,
                    submission.problem_index,
                    submission.problem_name,
                    submission.verdict,
                    submission.programming_language,
                    submission.creation_time_seconds,
                ),
            )
            await db.commit()
            submission.id = cursor.lastrowid
            return submission

    async def create_many(self, submissions: list[Submission]) -> None:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            for submission in submissions:
                await db.execute(
                    """INSERT OR IGNORE INTO submissions
                       (user_id, submission_id, contest_id, problem_index, problem_name,
                        verdict, programming_language, creation_time_seconds)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        submission.user_id,
                        submission.submission_id,
                        submission.contest_id,
                        submission.problem_index,
                        submission.problem_name,
                        submission.verdict,
                        submission.programming_language,
                        submission.creation_time_seconds,
                    ),
                )
            await db.commit()

    async def find_by_user_id(self, user_id: int) -> list[Submission]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM submissions WHERE user_id = ? ORDER BY creation_time_seconds DESC",
                (user_id,),
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    Submission(
                        id=row["id"],
                        user_id=row["user_id"],
                        submission_id=row["submission_id"],
                        contest_id=row["contest_id"],
                        problem_index=row["problem_index"],
                        problem_name=row["problem_name"],
                        verdict=row["verdict"],
                        programming_language=row["programming_language"],
                        creation_time_seconds=row["creation_time_seconds"],
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
    ) -> list[Submission]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM submissions WHERE user_id = ? ORDER BY creation_time_seconds DESC LIMIT ?",
                (user_id, limit),
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    Submission(
                        id=row["id"],
                        user_id=row["user_id"],
                        submission_id=row["submission_id"],
                        contest_id=row["contest_id"],
                        problem_index=row["problem_index"],
                        problem_name=row["problem_name"],
                        verdict=row["verdict"],
                        programming_language=row["programming_language"],
                        creation_time_seconds=row["creation_time_seconds"],
                        created_at=datetime.fromisoformat(row["created_at"])
                        if row["created_at"]
                        else None,
                        updated_at=datetime.fromisoformat(row["updated_at"])
                        if row["updated_at"]
                        else None,
                    )
                    for row in rows
                ]
