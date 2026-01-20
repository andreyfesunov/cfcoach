import aiosqlite
from pathlib import Path
from typing import Optional
import json

from domain.models.problem import Problem
from domain.repositories.problems import ProblemRepository


class ProblemRepositoryImpl(ProblemRepository):
    def __init__(self, db_path: Path):
        self.db_path = db_path

    async def _init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS problems (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contest_id INTEGER,
                    problem_index TEXT,
                    name TEXT NOT NULL,
                    problem_type TEXT,
                    points REAL,
                    rating INTEGER,
                    tags TEXT,
                    UNIQUE(contest_id, problem_index)
                )
                """
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_problems_contest_id ON problems(contest_id)"
            )
            await db.commit()

    async def find_by_contest_and_index(
        self, contest_id: int, problem_index: str
    ) -> Optional[Problem]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM problems WHERE contest_id = ? AND problem_index = ?",
                (contest_id, problem_index),
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    tags = json.loads(row["tags"]) if row["tags"] else []
                    return Problem(
                        id=row["id"],
                        contest_id=row["contest_id"],
                        problem_index=row["problem_index"],
                        name=row["name"],
                        problem_type=row["problem_type"],
                        points=row["points"],
                        rating=row["rating"],
                        tags=tags,
                    )
                return None

    async def create(self, problem: Problem) -> Problem:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """INSERT OR IGNORE INTO problems
                   (contest_id, problem_index, name, problem_type, points, rating, tags)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    problem.contest_id,
                    problem.problem_index,
                    problem.name,
                    problem.problem_type,
                    problem.points,
                    problem.rating,
                    json.dumps(problem.tags),
                ),
            )
            await db.commit()
            if cursor.lastrowid:
                problem.id = cursor.lastrowid
            return problem

    async def create_many(self, problems: list[Problem]) -> None:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            for problem in problems:
                await db.execute(
                    """INSERT OR IGNORE INTO problems
                       (contest_id, problem_index, name, problem_type, points, rating, tags)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        problem.contest_id,
                        problem.problem_index,
                        problem.name,
                        problem.problem_type,
                        problem.points,
                        problem.rating,
                        json.dumps(problem.tags),
                    ),
                )
            await db.commit()

    async def find_by_contest_id(self, contest_id: int) -> list[Problem]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM problems WHERE contest_id = ?", (contest_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    Problem(
                        id=row["id"],
                        contest_id=row["contest_id"],
                        problem_index=row["problem_index"],
                        name=row["name"],
                        problem_type=row["problem_type"],
                        points=row["points"],
                        rating=row["rating"],
                        tags=json.loads(row["tags"]) if row["tags"] else [],
                    )
                    for row in rows
                ]
