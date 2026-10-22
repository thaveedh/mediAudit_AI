from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


@router.get("/")
def root():
    return {
        "status": "online",
        "service": "Prescription Audit API",
        "endpoints": {
            "health": "/api/health",
            "ask": "/api/ask",
            "docs": "/docs"
        }
    }


@router.get("/api/health")
def health_check():
    return {
        "status": "ready",
        "ready": True,
        "demo": False,
        "detail": None,
        "message": "Prescription Audit Backend is running"
    }


@router.post("/api/ask")
def ask_question(data: dict):
    question = data.get("question", "")

    print(f"Received question: {question}")

    # Lazy import so server boots in milliseconds
    from rag import ask

    answer = ask(question)

    return {
        "question": question,
        "answer": answer
    }
