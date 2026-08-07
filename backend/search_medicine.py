from vector_db.chroma_db import collection

offset = 0
limit = 100

found = False

while True:

    results = collection.get(
        limit=limit,
        offset=offset
    )

    if not results["metadatas"]:
        break

    for meta in results["metadatas"]:

        medicine = meta["medicine"].lower()

        if "acetaminophen" in medicine or "paracetamol" in medicine:
            print(meta["medicine"])
            found = True

    offset += limit

if not found:
    print("No standalone Acetaminophen/Paracetamol medicine found.")