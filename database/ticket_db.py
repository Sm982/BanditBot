import sqlite3
import aiosqlite
import os
from logger import logger

class ticketDatabase:
    def __init__(self, db_path="data/ticket.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    async def initialize(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
            CREATE TABLE IF NOT EXISTS ticketing_db (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_number INTEGER UNIQUE,
                creator_user_id BIGINT,
                interrogate_user_id BIGINT,
                status TEXT DEFAULT 'open',
                created_at TIMESTAMP,
                closed_at TIMESTAMP,
                assigned_to BIGINT
            )
        """)
            await db.commit()
            logger.info("Ticketing database initialized")

    async def next_ticket_number(self):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(""" 
                SELECT MAX(ticket_number) FROM ticketing_db
            """)
            result = await cursor.fetchone()

            next_number = (result[0] or 0) + 1
            return next_number
        
    async def create_ticket(self, creator_user_id, created_at):
        try:
            ticket_number = await self.next_ticket_number()

            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(""" 
                    INSERT INTO ticketing_db(ticket_number, creator_user_id, created_at)
                    VALUES (?, ?, ?)
                """, (ticket_number, creator_user_id, created_at))
                await db.commit()
            logger.info(f"Created ticket #{ticket_number} for user {creator_user_id}")
            return ticket_number
        
        except Exception as e:
            logger.error(f"Error creating ticket {e}")
            return None
        
    async def get_ticket_by_number(self, ticket_number):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(""" 
                SELECT * FROM ticketing_db WHERE ticket_number = ?
            """, (ticket_number,))
            return await cursor.fetchone()
        
    async def check_if_claimed_ticket(self, ticket_number):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(""" 
                SELECT assigned_to FROM ticketing_db WHERE ticket_number = ?
            """, (ticket_number))
            return await cursor.fetchone()
        
    async def assign_ticket(self, ticket_number, assigned_to_user_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(""" 
                UPDATE ticketing_db SET assigned_to = ? WHERE ticket_number = ?
            """, (assigned_to_user_id, ticket_number))
            await db.commit()

        
    async def update_ticket_status(self, ticket_number, status, closed_at=None):
        async with aiosqlite.connect(self.db_path) as db:
            if closed_at:
                await db.execute(""" 
                    UPDATE ticketing_db
                    SET status = ?, closed_at = ?
                    WHERE ticket_number = ?
                """, (status, closed_at, ticket_number))
            else:
                await db.execute(""" 
                    UPDATE ticketing_db
                    SET status = ?
                    WHERE ticket_number = ?
                """, (status, ticket_number))
            await db.commit()

    async def assign_ticket(self, ticket_number, assigned_to):
        print('WRITE ME CODE')

    async def check_user_tickets(self, what_user_id):
        print('WRITE ME CODE')

    
    
