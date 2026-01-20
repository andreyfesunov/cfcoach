import aiosqlite
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from domain.models.recommendation_cache import RecommendationCache
from domain.repositories.recommendation_cache import RecommendationCacheRepository


class RecommendationCacheRepositoryImpl(RecommendationCacheRepository):
    def __init__(self, db_path: Path):
        self.db_path = db_path

    async def _init_db(self):
        async with aiosqlite.connect(self.db_path, timeout=30.0) as db:
            await db.execute("PRAGMA journal_mode=WAL")
            await db.execute("PRAGMA busy_timeout=30000")
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS recommendation_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    recommender_type TEXT NOT NULL,
                    problem_ids TEXT NOT NULL,
                    scores TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    UNIQUE(user_id, recommender_type)
                )
                """
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_cache_user_id ON recommendation_cache(user_id)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_cache_expires_at ON recommendation_cache(expires_at)"
            )
            await db.commit()

    async def find_by_user_and_type(
        self, user_id: int, recommender_type: str
    ) -> Optional[RecommendationCache]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path, timeout=30.0) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM recommendation_cache WHERE user_id = ? AND recommender_type = ? AND (expires_at IS NULL OR expires_at > datetime('now'))",
                (user_id, recommender_type),
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return RecommendationCache(
                        id=row["id"],
                        user_id=row["user_id"],
                        recommender_type=row["recommender_type"],
                        problem_ids=json.loads(row["problem_ids"]),
                        scores=json.loads(row["scores"]),
                        created_at=datetime.fromisoformat(row["created_at"])
                        if row["created_at"]
                        else None,
                        expires_at=datetime.fromisoformat(row["expires_at"])
                        if row["expires_at"]
                        else None,
                    )
                return None

    async def create(self, cache: RecommendationCache) -> RecommendationCache:
        await self._init_db()
        async with aiosqlite.connect(self.db_path, timeout=30.0) as db:
            expires_at_str = cache.expires_at.isoformat() if cache.expires_at else None
            cursor = await db.execute(
                """INSERT OR REPLACE INTO recommendation_cache
                   (user_id, recommender_type, problem_ids, scores, expires_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    cache.user_id,
                    cache.recommender_type,
                    json.dumps(cache.problem_ids),
                    json.dumps(cache.scores),
                    expires_at_str,
                ),
            )
            await db.commit()
            if cursor.lastrowid:
                cache.id = cursor.lastrowid
            return cache

    async def update(self, cache: RecommendationCache) -> RecommendationCache:
        await self._init_db()
        async with aiosqlite.connect(self.db_path, timeout=30.0) as db:
            expires_at_str = cache.expires_at.isoformat() if cache.expires_at else None
            await db.execute(
                """UPDATE recommendation_cache
                   SET problem_ids = ?, scores = ?, expires_at = ?
                   WHERE id = ?""",
                (
                    json.dumps(cache.problem_ids),
                    json.dumps(cache.scores),
                    expires_at_str,
                    cache.id,
                ),
            )
            await db.commit()
            return cache

    async def delete_expired(self) -> None:
        await self._init_db()
        async with aiosqlite.connect(self.db_path, timeout=30.0) as db:
            await db.execute(
                "DELETE FROM recommendation_cache WHERE expires_at IS NOT NULL AND expires_at < datetime('now')"
            )
            await db.commit()

    async def delete_by_user_and_type(
        self, user_id: int, recommender_type: str
    ) -> None:
        await self._init_db()
        async with aiosqlite.connect(self.db_path, timeout=30.0) as db:
            await db.execute(
                "DELETE FROM recommendation_cache WHERE user_id = ? AND recommender_type = ?",
                (user_id, recommender_type),
            )
            await db.commit()
