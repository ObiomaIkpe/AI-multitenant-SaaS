from pydantic_settings import BaseSettings, SettingsConfigDict
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE_PATH = os.path.join(BASE_DIR, "..", ".env")

class Settings(BaseSettings):
    
    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH, 
        extra='ignore'
    )

    PROJECT_NAME: str = "RAG SaaS Demo"
    
    # Security/JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    TENANT_ID_FIELD: str = "tenant_id"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    DATABASE_URL: str

    # Qdrant
    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION: str = "multi_tenant_rag"

    # OpenAI
    OPENAI_API_KEY: str
    GEMINI_API_KEY: str = ""
    
    # Embedding Model (NEW)
    EMBEDDING_MODEL: str = "local"

settings = Settings()

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
if settings.GEMINI_API_KEY:
    os.environ["GEMINI_API_KEY"] = settings.GEMINI_API_KEY