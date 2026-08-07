from embedding import get_embedding

embedding = get_embedding("Paracetamol is used to reduce fever.")

print(type(embedding))
print(len(embedding))
print(embedding[:5])