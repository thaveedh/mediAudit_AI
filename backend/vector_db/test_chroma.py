from chroma_db import collection
from embedding import get_embedding

text = "Paracetamol is used to reduce fever and relieve mild pain."

embedding = get_embedding(text)

collection.add(
    ids=["doc2"],
    documents=[text],
    embeddings=[embedding]
)

print(collection.count())