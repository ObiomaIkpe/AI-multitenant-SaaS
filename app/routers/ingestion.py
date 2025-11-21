from fastapi import APIRouter

# Initialize the router object
router = APIRouter()

@router.get("/status")
async def get_ingestion_status():
    return {"status": "Ingestion router initialized."}