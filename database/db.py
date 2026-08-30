import aiosqlite
from datetime import datetime
from config import DB_PATH


class Database:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    async def init(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    type TEXT,
                    amount REAL,
                    category TEXT,
                    date TEXT
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT
                )
            ''')
            await db.commit()

    async def add_user(self, user_id: int, username: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
                (user_id, username)
            )
            await db.commit()

    async def add_transaction(self, user_id: int, t_type: str, amount: float, category: str):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO transactions (user_id, type, amount, category, date) VALUES (?, ?, ?, ?, ?)",
                (user_id, t_type, amount, category, date)
            )
            await db.commit()

    async def get_monthly_report(self, user_id: int, year_month: str):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """SELECT type, SUM(amount) as total, category FROM transactions
                   WHERE user_id = ? AND strftime('%Y-%m', date) = ?
                   GROUP BY type, category""",
                (user_id, year_month)
            ) as cursor:
                return await cursor.fetchall()

    async def get_total_report(self, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT type, SUM(amount) as total FROM transactions WHERE user_id = ? GROUP BY type",
                (user_id,)
            ) as cursor:
                return await cursor.fetchall()

    async def get_all_transactions(self, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT type, amount, category, date FROM transactions WHERE user_id = ? ORDER BY date DESC",
                (user_id,)
            ) as cursor:
                return await cursor.fetchall()