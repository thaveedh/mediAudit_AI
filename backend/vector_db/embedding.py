import os

_model = None


def get_embedding(text: str):
    global _model

    if os.getenv("DISABLE_HEAVY_EMBEDDING", "false").lower() in ("true", "1"):
        return [0.0] * 384

    try:
        if _model is None:
            os.environ["OMP_NUM_THREADS"] = "1"
            os.environ["MKL_NUM_THREADS"] = "1"
            os.environ["TOKENIZERS_PARALLELISM"] = "false"
            from sentence_transformers import SentenceTransformer

            local_only = os.getenv("EMBEDDING_LOCAL_FILES_ONLY", "false").lower() in ("true", "1")
            _model = SentenceTransformer(
                "BAAI/bge-small-en-v1.5",
                local_files_only=local_only
            )
        return _model.encode(
            text,
            normalize_embeddings=True
        ).tolist()
    except Exception as e:
        print(f"Embedding generation error: {e}")
        return [0.0] * 384
