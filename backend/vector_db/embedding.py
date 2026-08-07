from sentence_transformers import SentenceTransformer

# Load model only from local cache
model = SentenceTransformer(
    "BAAI/bge-small-en-v1.5",
    local_files_only=True
)


def get_embedding(text: str):
    return model.encode(
        text,
        normalize_embeddings=True
    ).tolist()