from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from llama_index.core import VectorStoreIndex
from llama_index.core.vector_stores.types import MetadataFilters, ExactMatchFilter
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.postprocessor import SentenceTransformerRerank

from app.core.security import get_current_tenant_id
from app.dependencies.rag import get_vector_index

router = APIRouter()

# Pydantic schema for the user's query input
class QueryRequest(BaseModel):
    query: str = Field(..., description="The natural language question for the RAG system.")

# Pydantic schema for the RAG response
class QueryResponse(BaseModel):
    answer: str = Field(..., description="The generated answer from the LLM.")
    source_file: str = Field(..., description="The primary document file name used as context.")

# --- The main secure query endpoint ---
@router.post("/ask", response_model=QueryResponse)
async def ask_question(
    request: QueryRequest,
    # SECURE DEPENDENCY: Get tenant_id from the valid JWT
    tenant_id: str = Depends(get_current_tenant_id),
    index: VectorStoreIndex = Depends(get_vector_index)
):
    try:
        # 1. CONSTRUCT THE SECURITY FILTER
        # This is the core of multi-tenancy security. The filter forces Qdrant to 
        # only search within data nodes that have the matching tenant_id metadata.
        tenant_filter = MetadataFilters(
            filters=[
                ExactMatchFilter(key="tenant_id", value=tenant_id)
            ]
        )
        
        # 2. CREATE THE RAG PIPELINE
        
        # A. RETRIEVER: Set up the retriever to use the security filter
        retriever = index.as_retriever(
            similarity_top_k=5, # Get 5 initial candidates
            filters=tenant_filter # APPLY THE CRUCIAL TENANCY FILTER HERE
        )

        # B. POST-PROCESSOR (Reranker - V1.5 Implementation)
        # We integrate the Reranker to boost relevance (as discussed).
        # Note: You need to install the 'sentence-transformers' package for this.
        reranker = SentenceTransformerRerank(
            model="cross-encoder/ms-marco-TinyBERT-L-2", # A fast, effective reranking model
            top_n=3 # Keep the best 3 chunks for the LLM
        )
        
        # C. QUERY ENGINE: Compose the pipeline
        query_engine = index.as_query_engine(
            retriever=retriever,
            node_postprocessors=[reranker],
        )

        # 3. EXECUTE QUERY AND GENERATE RESPONSE
        response = await query_engine.aquery(request.query)

        # 4. Extract source information from the best node
        source_node = response.source_nodes[0].node
        source_file = source_node.metadata.get('file_name', 'Unknown Source')

        return QueryResponse(
            answer=str(response),
            source_file=source_file
        )

    except Exception as e:
        print(f"Query Error for Tenant {tenant_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during query processing."
        )

# Placeholder route to confirm initialization
@router.get("/status")
async def get_query_status():
    return {"status": "Query router initialized and awaiting secure queries."}