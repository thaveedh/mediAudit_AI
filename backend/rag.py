from vector_db.retriever import retrieve
from llm.generator import generate_rag_answer


def ask(question):

    # For now, treat the user's question itself as the medicine query
    medicine = question.strip()

    results = retrieve(
        query=question,
        medicine=medicine,
        k=20
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    context = ""

    for doc, meta in zip(documents, metadatas):

        context += f"""
Medicine: {meta['medicine']}
Section: {meta['section']}

{doc}

--------------------------------------------------
"""

    answer = generate_rag_answer(context, question)

    return answer