
from pathlib import Path
from blue_next.config.settings import DATA_DIR

class VectorMemory:
    """ChromaDB + FAISS friendly wrapper. Falls back to simple text search if not installed."""
    def __init__(self):
        self.items = []
        self.backend = "simple"
        self.chroma = None
        try:
            import chromadb
            self.chroma = chromadb.PersistentClient(path=str(DATA_DIR / "chroma"))
            self.collection = self.chroma.get_or_create_collection("blue_memory")
            self.backend = "chromadb"
        except Exception:
            self.collection = None

    def add(self, text, meta=None):
        meta = meta or {}
        if self.collection:
            idx = str(abs(hash(text)))
            try:
                self.collection.upsert(ids=[idx], documents=[text], metadatas=[meta])
                return
            except Exception:
                pass
        self.items.append((text, meta))

    def search(self, query, n=5):
        if self.collection:
            try:
                r = self.collection.query(query_texts=[query], n_results=n)
                return r.get("documents", [[]])[0]
            except Exception:
                pass
        q = query.lower()
        scored = [(sum(1 for w in q.split() if w in text.lower()), text) for text, _ in self.items]
        return [t for s,t in sorted(scored, reverse=True)[:n] if s > 0]

VECTOR_MEMORY = VectorMemory()
