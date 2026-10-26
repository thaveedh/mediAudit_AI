from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


@router.get("/")
def root():
    return {
        "status": "online",
        "service": "Prescription Audit API",
        "dataset": "FDA DailyMed (8,118 Records Indexed)",
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
        "dataset_records": 8118,
        "message": "Prescription Audit Backend is connected to FDA DailyMed dataset"
    }


@router.post("/api/ask")
def ask_question(data: dict):
    question = data.get("question", "")

    print(f"Received question: {question}")

    from rag import ask_with_metadata

    result = ask_with_metadata(question)

    return {
        "question": question,
        "answer": result["answer"],
        "provenance": result.get("metadata", {})
    }
