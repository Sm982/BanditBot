import sqlite3
import aiosqlite
import os
from logger import logger

class ticketDatabase:
    def __init__(self, db_path="data/ticket.db"):
        self.db_path = db_path
        self.db = None
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    async def initialize(self):
        self.db = await aiosqlite.connect(self.db_path)

        await self.db.execute("PRAGMA journal_mode=WAL")
        await self.db.execute("PRAGMA synchronous=NORMAL")
        
        await self.db.execute("""
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
        await self.db.commit()
        logger.info("Ticketing database initialized")

    async def next_ticket_number(self):
        cursor = await self.db.execute("SELECT MAX(ticket_number) FROM ticketing_db")
        result = await cursor.fetchone()
        await cursor.close()
        return (result[0] or 0) + 1
        
    async def create_ticket(self, creator_user_id, created_at):
        try:
            ticket_number = await self.next_ticket_number()
            await self.db.execute("""INSERT INTO ticketing_db(ticket_number, creator_user_id, created_at) VALUES (?, ?, ?)""", (ticket_number, creator_user_id, created_at))
            await self.db.commit()
            logger.info(f"Created ticket #{ticket_number} for user {creator_user_id}")
            return ticket_number
        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            await self.db.rollback()
            return None
        
    async def get_ticket_by_number(self, ticket_number):
        cursor = await self.db.execute("""SELECT * FROM ticketing_db WHERE ticket_number = ? """, (ticket_number,))
        result = await cursor.fetchone()
        await cursor.close()
        return result
        
    async def check_if_claimed_ticket(self, ticket_number):
        cursor = await self.db.execute("""SELECT assigned_to FROM ticketing_db WHERE ticket_number = ? """, (ticket_number,))
        result = await cursor.fetchone()
        await cursor.close()
        return result
        
    async def assign_ticket(self, ticket_number, assigned_to_user_id):
        await self.db.execute("""UPDATE ticketing_db SET assigned_to = ? WHERE ticket_number = ? """, (assigned_to_user_id, ticket_number))
        await self.db.commit()

    async def update_ticket_status(self, ticket_number, status, closed_at=None):
        if closed_at:
            await self.db.execute("""UPDATE ticketing_db SET status = ?, closed_at = ? WHERE ticket_number = ? """, (status, closed_at, ticket_number))
        else:
            await self.db.execute("""UPDATE ticketing_db SET status = ? WHERE ticket_number = ? """, (status, ticket_number))
        await self.db.commit()

    async def check_user_tickets(self, what_user_id):
        logger.debug('WRITE THIS CODE SNIPPIT')

    
    
