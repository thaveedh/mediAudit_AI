from utils.query_normalizer import normalize_query
from vector_db.embedding import get_embedding
from vector_db.chroma_db import get_collection


def retrieve(query: str, medicine: str = None, k: int = 20):

    print("=" * 60)
    print("USER QUERY")
    print(query)

    col = get_collection()
    if col is None:
        print("ChromaDB is unavailable")
        return {"documents": [[]], "metadatas": [[]]}

    # Normalize query
    normalized_query = normalize_query(query)

    print("\nNORMALIZED QUERY")
    print(normalized_query)

    # Generate query embedding
    query_embedding = get_embedding(normalized_query)

    print("\nEmbedding Generated")
    print("Vector Length:", len(query_embedding))

    # Build filter
    where_filter = None

    if medicine:
        where_filter = {
            "medicine": medicine
        }

        print("\nMEDICINE FILTER")
        print(medicine)

    try:
        results = col.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=where_filter
        )
    except Exception as e:
        print(f"ChromaDB query error: {e}")
        return {"documents": [[]], "metadatas": [[]]}

    num_found = len(results["documents"][0]) if results.get("documents") and results["documents"] else 0
    print("\nRESULTS FOUND:", num_found)

    return results
