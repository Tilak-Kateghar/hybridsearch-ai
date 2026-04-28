import sqlite3
from bm25_store import BM25Store
from faiss_store import FAISSStore
from hybrid_search import HybridSearch
from embeddings import model

DB_FILE = "rag.db"


class UserStore:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            content TEXT
        )
        """)

        self.conn.commit()

        self.user_cache = {}

    def get_user(self, user_id):
        if user_id in self.user_cache:
            return self.user_cache[user_id]

        self.cursor.execute(
            "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
            (user_id,)
        )
        self.conn.commit()

        self.cursor.execute(
            "SELECT content FROM documents WHERE user_id=?",
            (user_id,)
        )
        docs = [row[0] for row in self.cursor.fetchall()]

        bm25 = BM25Store()
        faiss = FAISSStore(model)

        if docs:
            bm25.build(docs)
            faiss.build(docs)
            hybrid = HybridSearch(bm25, faiss)
        else:
            hybrid = None

        user_obj = {
            "documents": docs,
            "bm25": bm25,
            "faiss": faiss,
            "hybrid": hybrid,
            "last_video": None
        }

        self.user_cache[user_id] = user_obj
        return user_obj

    def save_documents(self, user_id, documents):
        self.cursor.execute(
            "DELETE FROM documents WHERE user_id=?",
            (user_id,)
        )

        self.cursor.executemany(
            "INSERT INTO documents (user_id, content) VALUES (?, ?)",
            [(user_id, doc) for doc in documents]
        )

        self.conn.commit()

        if user_id in self.user_cache:
            del self.user_cache[user_id]


user_store = UserStore()