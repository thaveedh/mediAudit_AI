import os

_client = None
_collection = None


def get_collection():
    global _client, _collection
    if _collection is None:
        try:
            import chromadb

            # Check both relative paths
            db_path = "./chroma_storage"
            if not os.path.exists(db_path) and os.path.exists("backend/chroma_storage"):
                db_path = "backend/chroma_storage"

            _client = chromadb.PersistentClient(path=db_path)
            _collection = _client.get_or_create_collection(
                name="medical_documents"
            )
        except Exception as e:
            print(f"ChromaDB initialization error: {e}")
            return None
    return _collection


class LazyCollection:
    def __getattr__(self, name):
        col = get_collection()
        if col is None:
            raise RuntimeError("ChromaDB collection is not available")
        return getattr(col, name)


collection = LazyCollection()
