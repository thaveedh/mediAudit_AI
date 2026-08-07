import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from vector_db.retriever import retrieve

query = input("Enter your query: ")

results = retrieve(query)

print("\n" + "=" * 60)
print("TOP MATCHES")
print("=" * 60)

documents = results["documents"][0]
metadatas = results["metadatas"][0]
distances = results["distances"][0]

for i in range(len(documents)):

    print(f"\nResult {i+1}")
    print("-" * 50)

    print("Medicine :", metadatas[i]["medicine"])
    print("Section  :", metadatas[i]["section"])
    print("Distance :", distances[i])

    print("\nContent:\n")
    print(documents[i][:1000])

    print("\n" + "=" * 60)