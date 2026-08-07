from utils.query_normalizer import normalize_query
from vector_db.embedding import get_embedding
from vector_db.chroma_db import collection


def retrieve(query: str, k: int = 5):

    print("=" * 60)
    print("USER QUERY")
    print(query)

    # ==========================================
    # Normalize User Query
    # ==========================================
    normalized_query = normalize_query(query)

    print("\nNORMALIZED QUERY")
    print(normalized_query)

    # ==========================================
    # Generate Query Embedding
    # ==========================================
    query_embedding = get_embedding(normalized_query)

    print("\nEmbedding Generated")
    print("Vector Length:", len(query_embedding))

    # ==========================================
    # Search ChromaDB
    # ==========================================
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k
    )

    return results