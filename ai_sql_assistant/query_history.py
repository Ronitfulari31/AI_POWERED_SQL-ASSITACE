import sqlite3
from datetime import datetime
from pathlib import Path

class QueryHistory:
    def __init__(self):
        self.db_path = Path(__file__).parent / 'data' / 'query_history.db'
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def init_db(self):
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    natural_query TEXT,
                    sql_query TEXT,
                    schema_name TEXT,
                    execution_time TIMESTAMP,
                    is_favorite BOOLEAN DEFAULT 0
                )
            """)
            conn.commit()

    def add_query(self, natural_query: str, sql_query: str, schema_name: str):
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO query_history (natural_query, sql_query, schema_name, execution_time) VALUES (?, ?, ?, ?)",
                (natural_query, sql_query, schema_name, datetime.now())
            )
            conn.commit()

    def get_history(self, limit: int = 50):
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM query_history ORDER BY execution_time DESC LIMIT ?",
                (limit,)
            )
            return cursor.fetchall()

    def toggle_favorite(self, query_id: int):
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE query_history SET is_favorite = NOT is_favorite WHERE id = ?",
                (query_id,)
            )
            conn.commit()

    def get_favorites(self):
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM query_history WHERE is_favorite = 1 ORDER BY execution_time DESC")
            return cursor.fetchall()