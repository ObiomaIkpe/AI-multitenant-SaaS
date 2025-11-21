from fastapi import APIRouter

# Initialize the router object
router = APIRouter()

@router.get("/status")
async def get_query_status():
    return {"status": "Query router initialized."}