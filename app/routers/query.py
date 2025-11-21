from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List

# LlamaIndex Imports
from llama_index.core import VectorStoreIndex
from llama_index.core.vector_stores.types import MetadataFilters, ExactMatchFilter
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.vector_stores.qdrant import QdrantVectorStore 
from llama_index.core.settings import Settings 
from llama_index.llms.gemini import Gemini 
from llama_index.core.query_engine import RetrieverQueryEngine

# Core/Local Imports
from app.dependencies.common import get_qdrant_client_dependency, get_async_qdrant_client_dependency
from app.core.config import settings
from app.core.security import get_current_tenant_id
from qdrant_client import QdrantClient, AsyncQdrantClient

router = APIRouter()

# --- Pydantic Schema for Input and Output ---
class QueryRequest(BaseModel):
    query: str = Field(..., description="The natural language question for the RAG system.")

class QueryResponse(BaseModel):
    answer: str = Field(..., description="The generated answer from the LLM.")
    sources: List[str] = Field(..., description="A list of document chunks used as context.")

# --- The main secure query endpoint ---
@router.post("/ask", response_model=QueryResponse)
async def ask_question(
    request: QueryRequest,
    tenant_id: str = Depends(get_current_tenant_id),
    qdrant_client: QdrantClient = Depends(get_qdrant_client_dependency), 
    async_qdrant_client: AsyncQdrantClient = Depends(get_async_qdrant_client_dependency) 
):
    
    # 0. INITIAL SETUP AND CHECKS
    if not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="The GEMINI_API_KEY is not configured. Cannot generate response."
        )

    try:
        # Configure LLM globally before using the index/query engine
        Settings.llm = Gemini(
            model="gemini-2.0-flash-exp",
            api_key=settings.GEMINI_API_KEY
        )

        # 1. INITIALIZE INDEX FROM QDRANT CLIENT
        vector_store = QdrantVectorStore(
            client=qdrant_client, 
            aclient=async_qdrant_client,
            collection_name=settings.QDRANT_COLLECTION
        )
        index = VectorStoreIndex.from_vector_store(vector_store)

        # 2. CONSTRUCT THE SECURITY FILTER
        tenant_filter = MetadataFilters(
            filters=[
                ExactMatchFilter(key="tenant_id", value=tenant_id)
            ]
        )
        
        # 3. CREATE THE RAG PIPELINE
        
        # A. RETRIEVER: Set up the retriever to use the security filter
        retriever = index.as_retriever(
            similarity_top_k=5, 
            filters=tenant_filter 
        )

        # B. POST-PROCESSOR (Reranker)
        reranker = SentenceTransformerRerank(
            model="cross-encoder/ms-marco-TinyBERT-L-2",
            top_n=3
        )
        
        # C. QUERY ENGINE: Compose the pipeline
        query_engine = RetrieverQueryEngine(
            retriever=retriever,
            node_postprocessors=[reranker],
        )

        # 4. EXECUTE QUERY AND GENERATE RESPONSE
        response = await query_engine.aquery(request.query)

        # 5. Extract sources from the retrieved nodes
        sources = [
            f"File: {node.metadata.get('file_name', 'N/A')} - Content: {node.text[:150]}..."
            for node in response.source_nodes
        ]

        return QueryResponse(
            answer=str(response),
            sources=sources
        )

    except Exception as e:
        print(f"Query Error for Tenant {tenant_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during query processing: {type(e).__name__}"
        )

# Placeholder route to confirm initialization
@router.get("/status")
async def get_query_status():
    return {"status": "Query router initialized and awaiting secure queries."}