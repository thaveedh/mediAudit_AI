from vector_db.retriever import retrieve
from llm.generator import generate_rag_answer


def ask(question):
    medicine = question.strip()

    results = retrieve(
        query=question,
        medicine=medicine,
        k=20
    )

    documents = results["documents"][0]

    context = ""
    for doc in documents:
        context += f"{doc}\n\n"

    answer = generate_rag_answer(context.strip(), question)
    return answer
