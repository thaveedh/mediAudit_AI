from fastapi import APIRouter
from pydantic import BaseModel

from rag import ask

router = APIRouter()


@router.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "message": "Prescription Audit Backend is running"
    }


@router.post("/api/ask")
def ask_question(data: dict):
    question = data.get("question", "")

    print(f"Received question: {question}")

    answer = ask(question)

    return {
        "question": question,
        "answer": answer
    }