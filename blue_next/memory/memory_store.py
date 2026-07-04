
import json, sqlite3, time, hashlib
from pathlib import Path
from blue_next.config.settings import DATA_DIR

DB_PATH = DATA_DIR / "blue_memory.db"
JSON_PATH = DATA_DIR / "blue_memory.json"

class MemoryStore:
    def __init__(self):
        self.db_path = DB_PATH
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS events(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT, kind TEXT, key TEXT, value TEXT, meta TEXT
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS learned_commands(
            phrase TEXT PRIMARY KEY, meaning TEXT, updated_at TEXT
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS knowledge(
            id TEXT PRIMARY KEY, topic TEXT, summary TEXT, source TEXT, trusted INTEGER, added_at TEXT
        )""")
        conn.commit(); conn.close()

    def add_event(self, kind, key, value, meta=""):
        conn = sqlite3.connect(self.db_path); cur = conn.cursor()
        cur.execute("INSERT INTO events(ts,kind,key,value,meta) VALUES(?,?,?,?,?)",
                    (time.strftime("%Y-%m-%d %H:%M:%S"), kind, key, value, meta))
        conn.commit(); conn.close()

    def teach_command(self, phrase, meaning):
        conn = sqlite3.connect(self.db_path); cur = conn.cursor()
        cur.execute("INSERT OR REPLACE INTO learned_commands(phrase,meaning,updated_at) VALUES(?,?,?)",
                    (phrase.lower().strip(), meaning.lower().strip(), time.strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit(); conn.close()

    def get_learned_command(self, phrase):
        conn = sqlite3.connect(self.db_path); cur = conn.cursor()
        cur.execute("SELECT meaning FROM learned_commands WHERE phrase=?", (phrase.lower().strip(),))
        row = cur.fetchone(); conn.close()
        return row[0] if row else ""

    def last_event(self):
        conn = sqlite3.connect(self.db_path); cur = conn.cursor()
        cur.execute("SELECT kind,key,value,ts FROM events ORDER BY id DESC LIMIT 1")
        row = cur.fetchone(); conn.close()
        return row

    def save_knowledge(self, topic, summary, source, trusted=0):
        kid = hashlib.sha256((topic+source+summary).encode()).hexdigest()[:20]
        conn = sqlite3.connect(self.db_path); cur = conn.cursor()
        cur.execute("INSERT OR REPLACE INTO knowledge(id,topic,summary,source,trusted,added_at) VALUES(?,?,?,?,?,?)",
                    (kid, topic, summary, source, int(trusted), time.strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit(); conn.close()
        return kid

MEMORY = MemoryStore()
