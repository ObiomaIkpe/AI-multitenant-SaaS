from fastapi import FastAPI
from app.core.config import settings
from app.dependencies.common import setup_llama_index_settings
from app.routers import ingestion, query


#setup llama index environment before app setup.
setup_llama_index_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Secure multi-tenant SaaS Demo.",
    version="1.0.0"
)

app.include_router(ingestion.router, tags=["ingestion"])
app.include_router(query.router, tags=["query"])

@app.get("/", tags=["Health Check"])
def read_root():
    return {"message": "API is healthy"}
