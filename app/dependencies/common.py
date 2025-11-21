from qdrant_client import QdrantClient, AsyncQdrantClient
from llama_index.core import Settings
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from app.core.config import settings

# --- LlamaIndex Embedding Configuration ---
def setup_embedding_model():
    """Configure the embedding model based on settings."""
    embedding_choice = getattr(settings, 'EMBEDDING_MODEL', 'local').lower()
    
    if embedding_choice == "local":
        try:
            print("INFO: Configuring local embedding model (no API required)...")
            Settings.embed_model = HuggingFaceEmbedding(
                model_name="BAAI/bge-small-en-v1.5",
                cache_folder="./.embedding_cache"
            )
            print("✓ SUCCESS: Local embedding model (bge-small-en-v1.5) loaded successfully.")
            return
        except Exception as e:
            print(f"ERROR: Failed to initialize local embeddings: {e}")
            print("Falling back to OpenAI or Gemini...")
    
    if embedding_choice == "openai" or (embedding_choice == "local" and settings.OPENAI_API_KEY):
        if settings.OPENAI_API_KEY:
            try:
                print("INFO: Configuring OpenAI embedding model...")
                Settings.embed_model = OpenAIEmbedding(
                    model="text-embedding-3-small",
                    api_key=settings.OPENAI_API_KEY
                )
                print("✓ SUCCESS: OpenAI embedding model configured.")
                return
            except Exception as e:
                print(f"ERROR: Failed to initialize OpenAI embeddings: {e}")
    
    if settings.GEMINI_API_KEY:
        try:
            print("WARNING: Using Gemini embeddings - rate limits apply!")
            Settings.embed_model = GeminiEmbedding(
                model_name="embedding-001",
                api_key=settings.GEMINI_API_KEY
            )
            print("INFO: LlamaIndex configured to use GeminiEmbedding (embedding-001).")
        except Exception as e:
            print(f"ERROR: Failed to initialize GeminiEmbedding: {e}")
            raise RuntimeError("No valid embedding configuration found.")
    else:
        raise RuntimeError("No valid embedding configuration found.")

# Initialize embedding model at module load
setup_embedding_model()


# --- Qdrant Client Factory (called once in main.py lifespan) ---
def get_qdrant_client() -> QdrantClient:
    """Create sync Qdrant client"""
    return QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None,
        https=False
    )

def get_async_qdrant_client() -> AsyncQdrantClient:
    """Create async Qdrant client"""
    return AsyncQdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None,
        https=False
    )


# --- Dependencies for injection (return the global clients) ---
def get_qdrant_client_dependency():
    """Dependency to inject sync Qdrant client"""
    from app.main import qdrant_client
    return qdrant_client

def get_async_qdrant_client_dependency():
    """Dependency to inject async Qdrant client"""
    from app.main import async_qdrant_client
    return async_qdrant_client