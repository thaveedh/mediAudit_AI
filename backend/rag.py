from vector_db.retriever import retrieve
from llm.generator import generate_rag_answer


def ask(question):

    results = retrieve(question)

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    context = ""

    for doc, meta in zip(documents, metadatas):

        context += f"""
Medicine: {meta['medicine']}
Section: {meta['section']}

{doc[:1200]}

--------------------------------------------------

"""

    answer = generate_rag_answer(context, question)

    return answer