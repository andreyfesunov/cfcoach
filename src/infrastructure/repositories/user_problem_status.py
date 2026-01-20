import aiosqlite
from datetime import datetime
from pathlib import Path
from typing import Optional

from domain.models.user_problem_status import UserProblemStatus
from domain.repositories.user_problem_status import UserProblemStatusRepository


class UserProblemStatusRepositoryImpl(UserProblemStatusRepository):
    def __init__(self, db_path: Path):
        self.db_path = db_path

    async def _init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS user_problem_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    contest_id INTEGER,
                    problem_index TEXT,
                    solved INTEGER NOT NULL,
                    attempts_count INTEGER NOT NULL DEFAULT 0,
                    first_solved_time INTEGER,
                    last_attempt_time INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    UNIQUE(user_id, contest_id, problem_index)
                )
                """
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_problem_status_user_id ON user_problem_status(user_id)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_problem_status_contest_id ON user_problem_status(contest_id)"
            )
            await db.commit()

    async def find_by_user_and_problem(
        self, user_id: int, contest_id: Optional[int], problem_index: Optional[str]
    ) -> Optional[UserProblemStatus]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM user_problem_status WHERE user_id = ? AND contest_id = ? AND problem_index = ?",
                (user_id, contest_id, problem_index),
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return UserProblemStatus(
                        id=row["id"],
                        user_id=row["user_id"],
                        contest_id=row["contest_id"],
                        problem_index=row["problem_index"],
                        solved=bool(row["solved"]),
                        attempts_count=row["attempts_count"],
                        first_solved_time=row["first_solved_time"],
                        last_attempt_time=row["last_attempt_time"],
                        created_at=datetime.fromisoformat(row["created_at"])
                        if row["created_at"]
                        else None,
                        updated_at=datetime.fromisoformat(row["updated_at"])
                        if row["updated_at"]
                        else None,
                    )
                return None

    async def create(self, status: UserProblemStatus) -> UserProblemStatus:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """INSERT OR IGNORE INTO user_problem_status
                   (user_id, contest_id, problem_index, solved, attempts_count,
                    first_solved_time, last_attempt_time)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    status.user_id,
                    status.contest_id,
                    status.problem_index,
                    1 if status.solved else 0,
                    status.attempts_count,
                    status.first_solved_time,
                    status.last_attempt_time,
                ),
            )
            await db.commit()
            if cursor.lastrowid:
                status.id = cursor.lastrowid
            return status

    async def update(self, status: UserProblemStatus) -> UserProblemStatus:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """UPDATE user_problem_status
                   SET solved = ?, attempts_count = ?, first_solved_time = ?,
                       last_attempt_time = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (
                    1 if status.solved else 0,
                    status.attempts_count,
                    status.first_solved_time,
                    status.last_attempt_time,
                    status.id,
                ),
            )
            await db.commit()
            return status

    async def find_by_user_id(self, user_id: int) -> list[UserProblemStatus]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM user_problem_status WHERE user_id = ?",
                (user_id,),
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    UserProblemStatus(
                        id=row["id"],
                        user_id=row["user_id"],
                        contest_id=row["contest_id"],
                        problem_index=row["problem_index"],
                        solved=bool(row["solved"]),
                        attempts_count=row["attempts_count"],
                        first_solved_time=row["first_solved_time"],
                        last_attempt_time=row["last_attempt_time"],
                        created_at=datetime.fromisoformat(row["created_at"])
                        if row["created_at"]
                        else None,
                        updated_at=datetime.fromisoformat(row["updated_at"])
                        if row["updated_at"]
                        else None,
                    )
                    for row in rows
                ]

    async def find_solved_by_user_id(self, user_id: int) -> list[UserProblemStatus]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM user_problem_status WHERE user_id = ? AND solved = 1",
                (user_id,),
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    UserProblemStatus(
                        id=row["id"],
                        user_id=row["user_id"],
                        contest_id=row["contest_id"],
                        problem_index=row["problem_index"],
                        solved=bool(row["solved"]),
                        attempts_count=row["attempts_count"],
                        first_solved_time=row["first_solved_time"],
                        last_attempt_time=row["last_attempt_time"],
                        created_at=datetime.fromisoformat(row["created_at"])
                        if row["created_at"]
                        else None,
                        updated_at=datetime.fromisoformat(row["updated_at"])
                        if row["updated_at"]
                        else None,
                    )
                    for row in rows
                ]

    async def find_unsolved_by_user_id(self, user_id: int) -> list[UserProblemStatus]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM user_problem_status WHERE user_id = ? AND solved = 0",
                (user_id,),
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    UserProblemStatus(
                        id=row["id"],
                        user_id=row["user_id"],
                        contest_id=row["contest_id"],
                        problem_index=row["problem_index"],
                        solved=bool(row["solved"]),
                        attempts_count=row["attempts_count"],
                        first_solved_time=row["first_solved_time"],
                        last_attempt_time=row["last_attempt_time"],
                        created_at=datetime.fromisoformat(row["created_at"])
                        if row["created_at"]
                        else None,
                        updated_at=datetime.fromisoformat(row["updated_at"])
                        if row["updated_at"]
                        else None,
                    )
                    for row in rows
                ]
