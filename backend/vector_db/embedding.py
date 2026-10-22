import os

_model = None


def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        local_only = os.getenv("EMBEDDING_LOCAL_FILES_ONLY", "false").lower() in ("true", "1")
        _model = SentenceTransformer(
            "BAAI/bge-small-en-v1.5",
            local_files_only=local_only
        )
    return _model


def get_embedding(text: str):
    try:
        model = get_model()
        return model.encode(
            text,
            normalize_embeddings=True
        ).tolist()
    except Exception as e:
        print(f"Embedding generation error: {e}")
        # Return fallback zero vector if model fails to load
        return [0.0] * 384
