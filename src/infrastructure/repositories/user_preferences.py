import aiosqlite
from datetime import datetime
from pathlib import Path
from typing import Optional

from domain.models.user_preferences import UserPreferences
from domain.repositories.user_preferences import UserPreferencesRepository


class UserPreferencesRepositoryImpl(UserPreferencesRepository):
    def __init__(self, db_path: Path):
        self.db_path = db_path

    async def _init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE NOT NULL,
                    preferred_recommender_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
                """
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_preferences_user_id ON user_preferences(user_id)"
            )
            await db.commit()

    async def find_by_user_id(self, user_id: int) -> Optional[UserPreferences]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM user_preferences WHERE user_id = ?",
                (user_id,),
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return UserPreferences(
                        id=row["id"],
                        user_id=row["user_id"],
                        preferred_recommender_type=row["preferred_recommender_type"],
                        created_at=datetime.fromisoformat(row["created_at"])
                        if row["created_at"]
                        else None,
                        updated_at=datetime.fromisoformat(row["updated_at"])
                        if row["updated_at"]
                        else None,
                    )
                return None

    async def create(self, preferences: UserPreferences) -> UserPreferences:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """INSERT OR IGNORE INTO user_preferences
                   (user_id, preferred_recommender_type)
                   VALUES (?, ?)""",
                (preferences.user_id, preferences.preferred_recommender_type),
            )
            await db.commit()
            if cursor.lastrowid:
                preferences.id = cursor.lastrowid
            return preferences

    async def update(self, preferences: UserPreferences) -> UserPreferences:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """UPDATE user_preferences
                   SET preferred_recommender_type = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (preferences.preferred_recommender_type, preferences.id),
            )
            await db.commit()
            return preferences
