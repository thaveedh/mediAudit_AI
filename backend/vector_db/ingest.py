import json

from chroma_db import collection
from embedding import get_embedding

with open("../data/medicines.json", "r", encoding="utf-8") as f:
    medicines = json.load(f)

for medicine in medicines:
    text = f"""
Name: {medicine['name']}
Description: {medicine['description']}
Side Effects: {", ".join(medicine['side_effects'])}
Contraindications: {", ".join(medicine['contraindications'])}
"""

    collection.add(
        ids=[medicine["id"]],
        documents=[text],
        embeddings=[get_embedding(text)]
    )

print("Documents in DB:", collection.count())