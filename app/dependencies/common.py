from qdrant_client import QdrantClient
from llama_index.core.settings import Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from app.core.config import settings

# --- 1. Qdrant Client Dependency (Reusable across endpoints) ---

def get_qdrant_client() -> QdrantClient:
    """Initializes and returns the global QdrantClient instance."""
    client = QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
        prefer_grpc=True  # Recommended for performance
    )
    return client

# --- 2. LlamaIndex Global Settings Setup (Called once at startup) ---

def setup_llama_index_settings():
    """Sets the global service context for LlamaIndex."""
    
    # Configure Embedding Model
    Settings.embed_model = OpenAIEmbedding(
        api_key=settings.OPENAI_API_KEY
    )
    
    # Configure LLM (GPT-3.5-turbo is a good balance of cost and quality)
    Settings.llm = OpenAI(
        model="gpt-3.5-turbo",
        api_key=settings.OPENAI_API_KEY
    )
    
    # Set default chunking strategy (will be conditionally overridden in routers)
    Settings.chunk_size = 512
    Settings.chunk_overlap = 50