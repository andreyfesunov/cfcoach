import aiosqlite
from pathlib import Path
from typing import Optional

from domain.models.contest import Contest
from domain.repositories.contests import ContestRepository


class ContestRepositoryImpl(ContestRepository):
    def __init__(self, db_path: Path):
        self.db_path = db_path

    async def _init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS contests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contest_id INTEGER UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    contest_type TEXT,
                    phase TEXT,
                    frozen INTEGER,
                    duration_seconds INTEGER,
                    start_time_seconds INTEGER,
                    relative_time_seconds INTEGER,
                    prepared_by TEXT,
                    website_url TEXT,
                    description TEXT,
                    difficulty INTEGER,
                    kind TEXT,
                    icpc_region TEXT,
                    country TEXT,
                    city TEXT,
                    season TEXT
                )
                """
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_contests_contest_id ON contests(contest_id)"
            )
            await db.commit()

    async def find_by_contest_id(self, contest_id: int) -> Optional[Contest]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM contests WHERE contest_id = ?", (contest_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return Contest(
                        id=row["id"],
                        contest_id=row["contest_id"],
                        name=row["name"],
                        contest_type=row["contest_type"],
                        phase=row["phase"],
                        frozen=bool(row["frozen"])
                        if row["frozen"] is not None
                        else None,
                        duration_seconds=row["duration_seconds"],
                        start_time_seconds=row["start_time_seconds"],
                        relative_time_seconds=row["relative_time_seconds"],
                        prepared_by=row["prepared_by"],
                        website_url=row["website_url"],
                        description=row["description"],
                        difficulty=row["difficulty"],
                        kind=row["kind"],
                        icpc_region=row["icpc_region"],
                        country=row["country"],
                        city=row["city"],
                        season=row["season"],
                    )
                return None

    async def create(self, contest: Contest) -> Contest:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """INSERT OR IGNORE INTO contests
                   (contest_id, name, contest_type, phase, frozen, duration_seconds,
                    start_time_seconds, relative_time_seconds, prepared_by, website_url,
                    description, difficulty, kind, icpc_region, country, city, season)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    contest.contest_id,
                    contest.name,
                    contest.contest_type,
                    contest.phase,
                    1 if contest.frozen else 0 if contest.frozen is not None else None,
                    contest.duration_seconds,
                    contest.start_time_seconds,
                    contest.relative_time_seconds,
                    contest.prepared_by,
                    contest.website_url,
                    contest.description,
                    contest.difficulty,
                    contest.kind,
                    contest.icpc_region,
                    contest.country,
                    contest.city,
                    contest.season,
                ),
            )
            await db.commit()
            if cursor.lastrowid:
                contest.id = cursor.lastrowid
            return contest

    async def create_many(self, contests: list[Contest]) -> None:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            for contest in contests:
                await db.execute(
                    """INSERT OR IGNORE INTO contests
                       (contest_id, name, contest_type, phase, frozen, duration_seconds,
                        start_time_seconds, relative_time_seconds, prepared_by, website_url,
                        description, difficulty, kind, icpc_region, country, city, season)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        contest.contest_id,
                        contest.name,
                        contest.contest_type,
                        contest.phase,
                        1
                        if contest.frozen
                        else 0
                        if contest.frozen is not None
                        else None,
                        contest.duration_seconds,
                        contest.start_time_seconds,
                        contest.relative_time_seconds,
                        contest.prepared_by,
                        contest.website_url,
                        contest.description,
                        contest.difficulty,
                        contest.kind,
                        contest.icpc_region,
                        contest.country,
                        contest.city,
                        contest.season,
                    ),
                )
            await db.commit()

    async def find_all(self) -> list[Contest]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM contests") as cursor:
                rows = await cursor.fetchall()
                return [
                    Contest(
                        id=row["id"],
                        contest_id=row["contest_id"],
                        name=row["name"],
                        contest_type=row["contest_type"],
                        phase=row["phase"],
                        frozen=bool(row["frozen"])
                        if row["frozen"] is not None
                        else None,
                        duration_seconds=row["duration_seconds"],
                        start_time_seconds=row["start_time_seconds"],
                        relative_time_seconds=row["relative_time_seconds"],
                        prepared_by=row["prepared_by"],
                        website_url=row["website_url"],
                        description=row["description"],
                        difficulty=row["difficulty"],
                        kind=row["kind"],
                        icpc_region=row["icpc_region"],
                        country=row["country"],
                        city=row["city"],
                        season=row["season"],
                    )
                    for row in rows
                ]
