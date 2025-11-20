from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

# --- Configuration ---
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "enterprise_knowledge"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# CRITICAL QUERIES
QUERY_TEXT = "Who is the primary contact for security and compliance issues?"

# Tenant IDs for testing security
CORRECT_TENANT_ID = "client_alpha_2025" 
WRONG_TENANT_ID = "client_beta_2025"

def query_data(tenant_id, query_text):
    """Queries Qdrant using manual embeddings and tenant_id filter."""
    
    # Initialize Clients
    client = QdrantClient(url=QDRANT_URL)
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    
    # Generate query embedding
    query_vector = embedding_model.encode(query_text).tolist()

    # Define the security filter
    tenant_filter = models.Filter(
        must=[
            models.FieldCondition(
                key="tenant_id",
                match=models.MatchValue(value=tenant_id)
            )
        ]
    )

    # Perform the secure search using query_points (NOT query)
    search_result = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,  # Pass the vector here
        query_filter=tenant_filter,
        limit=1,
        with_payload=True
    )
    
    return search_result.points

if __name__ == "__main__":
    print(f"--- Querying Data for RAG System ---")

    # TEST 1: ISOLATION TEST (USING WRONG TENANT ID)
    print("\n[TEST 1: UNSECURE SEARCH (Isolation Check)]")
    print(f"Simulating a query from WRONG TENANT: {WRONG_TENANT_ID}")
    
    results_wrong = query_data(WRONG_TENANT_ID, QUERY_TEXT)
    
    print(f"Results Found: {len(results_wrong)}")
    if not results_wrong:
        print("✅ **SUCCESS:** Data is isolated. The wrong tenant found nothing.")
    else:
        print("❌ **FAILURE:** Security Breach! Data was returned to the wrong tenant.")
        for result in results_wrong:
            print(f"  - Score: {result.score}")
            print(f"  - Text: {result.payload['text']}")

    # TEST 2: RETRIEVAL TEST (USING CORRECT TENANT ID)
    print("\n[TEST 2: SECURE SEARCH (Retrieval Check)]")
    print(f"Simulating a query from CORRECT TENANT: {CORRECT_TENANT_ID}")
    
    results_correct = query_data(CORRECT_TENANT_ID, QUERY_TEXT)
    
    print(f"Results Found: {len(results_correct)}")
    if results_correct:
        print("✅ **SUCCESS:** Data retrieved. The correct tenant found their data.")
        print("--- Retrieved Data ---")
        for result in results_correct:
            print(f"Score: {result.score:.4f}")
            print(f"Text: {result.payload['text']}")
    else:
        print("❌ **FAILURE:** The correct tenant could not retrieve their own data!")