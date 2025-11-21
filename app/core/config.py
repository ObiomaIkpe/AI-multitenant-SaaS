from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API
    PROJECT_NAME: str = "RAG SaaS Demo"
    
    # Security/JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    TENANT_ID_FIELD: str = "tenant_id"

    # Qdrant
    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION: str = "multi_tenant_rag"

    # OpenAI
    OPENAI_API_KEY: str

    # This is the crucial part that was likely missing or misnamed!
    class Config:
        env_file = ".env"

# --- THE MISSING/INCORRECT LINE ---
settings = Settings()
# ---------------------------------