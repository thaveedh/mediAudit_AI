from vector_db.retriever import retrieve
from llm.generator import generate_rag_answer


def ask_with_metadata(question):
    medicine = question.strip()

    results = retrieve(
        query=question,
        medicine=medicine,
        k=20
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    context = ""
    for doc in documents:
        context += f"{doc}\n\n"

    answer = generate_rag_answer(context.strip(), question)

    meta = metadatas[0] if metadatas else {}
    return {
        "answer": answer,
        "metadata": {
            "source": meta.get("source", "FDA DailyMed (8,118 records)"),
            "medicine": meta.get("medicine", ""),
            "section": meta.get("section", ""),
            "matched_records": meta.get("matched_records", 0)
        }
    }


def ask(question):
    return ask_with_metadata(question)["answer"]
