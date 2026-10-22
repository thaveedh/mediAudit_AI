from utils.query_normalizer import normalize_query
from vector_db.embedding import get_embedding
from vector_db.chroma_db import collection


def retrieve(query: str, medicine: str = None, k: int = 20):

    print("=" * 60)
    print("USER QUERY")
    print(query)

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

    # Search ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        where=where_filter
    )

    print("\nRESULTS FOUND:", len(results["documents"][0]))

    return results