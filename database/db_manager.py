import sqlite3
import aiosqlite
import os
from logger import logger

class CountingDatabase:
    def __init__(self, db_path="data/counting.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    async def initialize(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS counting_state (
                    guild_id INTEGER PRIMARY KEY,
                    current_count INTEGER DEFAULT 0,
                    last_user_id INTEGER,
                    highest_count INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()
            logger.info("Counting database initialized")

    async def get_counting_state(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT current_count, last_user_id, highest_count FROM counting_state WHERE guild_id = ?",
                (guild_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        'current_count': row[0],
                        'last_user_id': row[1],
                        'highest_count': row[2]
                    }
                else:
                    await self.update_counting_state(guild_id, 0, None, 0)
                    return {'current_count': 0, 'last_user_id': None, 'highest_count': 0}
    
    async def update_counting_state(self, guild_id, current_count, last_user_id, highest_count):
        """Update counting state for a guild"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO counting_state 
                (guild_id, current_count, last_user_id, highest_count, last_updated)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (guild_id, current_count, last_user_id, highest_count))
            await db.commit()
    
    async def reset_count(self, guild_id, keep_highest=True):
        """Reset current count but optionally keep highest"""
        state = await self.get_counting_state(guild_id)
        new_highest = state['highest_count'] if keep_highest else 0
        await self.update_counting_state(guild_id, 0, None, new_highest)