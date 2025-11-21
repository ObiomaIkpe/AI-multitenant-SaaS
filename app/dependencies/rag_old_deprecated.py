
from llama_index.core import VectorStoreIndex
from fastapi import Depends
from llama_index.vector_stores.qdrant import QdrantVectorStore
from app.core.config import settings
from .common import get_qdrant_client # Assuming get_qdrant_client is defined here

# 1. Define the Index as a Reusable Dependency
def get_vector_index(qdrant_client=Depends(get_qdrant_client)):
    """
    Creates a LlamaIndex VectorStoreIndex wrapper around the Qdrant client.
    """
    # Use the configured Qdrant collection
    vector_store = QdrantVectorStore(
        client=qdrant_client,
        collection_name=settings.QDRANT_COLLECTION,
    )

    # Initialize the index, which links LlamaIndex to the vector store
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        service_context=settings.SERVICE_CONTEXT # Use the global ServiceContext
    )
    return index