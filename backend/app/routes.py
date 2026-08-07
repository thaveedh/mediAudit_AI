from fastapi import APIRouter

router = APIRouter()


@router.post("/audit")
def audit_prescription(data: dict):
    medicine = data.get("medicine")

    print(f"Received medicine: {medicine}")

    return {
        "message": "Medicine received successfully",
        "medicine": medicine
    }