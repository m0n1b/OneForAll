import sqlite3
from datetime import datetime

class SQLiteCURD:
    def __init__(self, db_name="database.db"):
        self.db_name = db_name
        self._create_tables()
    
    def _connect(self):
        return sqlite3.connect(self.db_name)
    
    def _create_tables(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS task (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE NOT NULL,
                    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status INTEGER DEFAULT 0,
                    CONSTRAINT unique_url UNIQUE (url)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS domain (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain TEXT UNIQUE NOT NULL,
                    chat_id TEXT,
                    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status INTEGER DEFAULT 0,
                    start_time INTEGER  DEFAULT 0,
                    CONSTRAINT unique_domain UNIQUE (domain)
                    
                )
            ''')
            conn.commit()
    
    def insert_task(self, url):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO task (url) VALUES (?)", (url,))
            conn.commit()
    
    def insert_domain(self, domain, chat_id=None):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO domain (domain, chat_id) VALUES (?, ?)", (domain, chat_id))
            conn.commit()
    
    def get_oldest_pending_task(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, url, time, status FROM task WHERE status = 0 ORDER BY time ASC LIMIT 1")
            row = cursor.fetchone()
            return {"id": row[0], "url": row[1], "time": row[2], "status": row[3]} if row else None
    
    def get_oldest_pending_domain(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, domain, chat_id, time, status FROM domain WHERE status = 0 ORDER BY time ASC LIMIT 1")
            row = cursor.fetchone()
            return {"id": row[0], "domain": row[1], "chat_id": row[2], "time": row[3], "status": row[4]} if row else None
    
    def get_pending_task_count(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM task WHERE status = 0")
            return cursor.fetchone()[0]
            
            
    def get_pending_task_urls(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT url FROM task WHERE status = 0")
            return [row[0] for row in cursor.fetchall()]
    
    def get_pending_domain_names(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT domain FROM domain WHERE status = 0")
            return [row[0] for row in cursor.fetchall()]
            
            
            
    def get_pending_domain_count(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM domain WHERE status = 0")
            return cursor.fetchone()[0]
            
    def delet_time_out_domain(self,time):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM domain WHERE start_time > ? and start_time!=0", (time,))
            conn.commit()
    
    def get_runing_domain_count(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM domain WHERE status = 1")
            return cursor.fetchone()[0]
    
    def delete_task_by_id(self, task_id):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM task WHERE id = ?", (task_id,))
            conn.commit()
    
    def delete_domain_by_id(self, domain_id):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM domain WHERE id = ?", (domain_id,))
            conn.commit()
    
    def update_task_status(self, task_id, status):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE task SET status = ? WHERE id = ?", (status, task_id))
            conn.commit()
    
    def update_domain_status(self, domain_id, status,time):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE domain SET status = ? ,start_time =? WHERE id = ?", (status, time,domain_id))
            conn.commit()
    
    def clear_task_table(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM task")
            conn.commit()
    
    def clear_domain_table(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM domain")
            conn.commit()
