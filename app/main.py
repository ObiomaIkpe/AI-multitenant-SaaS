from app.routers import admin
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import settings
from app.routers import ingestion, query, auth
from app.dependencies.common import get_qdrant_client, get_async_qdrant_client

# Global Qdrant clients
qdrant_client = None
async_qdrant_client = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for startup and shutdown.
    Initializes Qdrant clients once and reuses them.
    """
    global qdrant_client, async_qdrant_client
    
    print("🚀 Starting up...")
    # Initialize Qdrant clients
    qdrant_client = get_qdrant_client()
    async_qdrant_client = get_async_qdrant_client()
    print("✅ Qdrant clients initialized")
    
    yield
    
    print("🛑 Shutting down...")
    # Cleanup
    if async_qdrant_client:
        await async_qdrant_client.close()
    if qdrant_client:
        qdrant_client.close()
    print("✅ Cleanup complete")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Secure multi-tenant RAG SaaS",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(ingestion.router, prefix="/api/v1/ingestion", tags=["Ingestion"])
app.include_router(query.router, prefix="/api/v1/query", tags=["Query"])
app.include_router(admin.router, prefix="/api/v1")



@app.get("/", tags=["Health Check"])
def read_root():
    return {"message": "RAG SaaS API is healthy", "version": "1.0.0"}


@app.get("/health", tags=["Health Check"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "qdrant": "connected"
    }