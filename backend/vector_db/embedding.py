import os
from sentence_transformers import SentenceTransformer

# In local dev with cached weights, EMBEDDING_LOCAL_FILES_ONLY can be "true"
# In cloud deployment (Render), defaults to False to automatically download the model
local_only = os.getenv("EMBEDDING_LOCAL_FILES_ONLY", "false").lower() in ("true", "1")

model = SentenceTransformer(
    "BAAI/bge-small-en-v1.5",
    local_files_only=local_only
)


def get_embedding(text: str):
    return model.encode(
        text,
        normalize_embeddings=True
    ).tolist()
