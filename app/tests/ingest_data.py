import uuid
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
from tqdm import tqdm # For visualizing progress

# --- Configuration ---
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "enterprise_knowledge"
# CRITICAL: This is the ID for the first client's data. 
# This must match the index you created.
TENANT_ID = "client_alpha_2025" 
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50

# Sample document text for Tenant Alpha
SAMPLE_DOCUMENT = """
The Alpha Corporation operates primarily in the energy sector, focusing on sustainable technologies. 
Our latest internal memo, released on November 15, 2025, mandates that all client interactions 
must strictly adhere to the new security protocol V3. This protocol is designed to ensure 
data separation between different customer environments, a key requirement for our SaaS offering. 
All access to the Qdrant database must include a mandatory payload filter using the 'tenant_id' keyword.
Failure to implement this filtering mechanism is a serious breach of the Alpha Corp Compliance Policy (ACCP).
The primary contact for security and compliance issues is Jane Doe at security@alphacorp.com.
"""

def split_text_into_chunks(text, chunk_size, chunk_overlap):
    """A simple character-level chunker."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start += chunk_size - chunk_overlap
    return chunks

def ingest_data():
    """Chunks text, embeds it, and upserts it to Qdrant with a tenant ID payload."""
    
    print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}...")
    # 1. Initialize Embedding Model (uses the PyTorch stack you installed)
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    
    # 2. Initialize Qdrant Client
    client = QdrantClient(url=QDRANT_URL)

    # 3. Process Document
    print(f"Chunking document and tagging with Tenant ID: {TENANT_ID}")
    text_chunks = split_text_into_chunks(SAMPLE_DOCUMENT, CHUNK_SIZE, CHUNK_OVERLAP)
    
    # 4. Generate Embeddings 
    vectors = embedding_model.encode(text_chunks, convert_to_numpy=True)
    
    points = []
    for i, (vector, chunk) in enumerate(zip(vectors, text_chunks)):
        # 5. Prepare the PointStruct
        point = models.PointStruct(
            id=i,  # Simple sequential ID for this example
            vector=vector.tolist(),
            payload={
                "text": chunk, 
                "tenant_id": TENANT_ID, # CRITICAL: The security tag
                "source": "internal_memo_2025" 
            }
        )
        points.append(point)

    # 6. Upsert Points to Qdrant (in a single batch)
    print(f"Uploading {len(points)} points to '{COLLECTION_NAME}'...")
    try:
        # CORRECTED LINE: Pass the 'points' list directly to client.upsert
        # We will let Qdrant's client handle its own progress logging or simply wait.
        operation_info = client.upsert(
            collection_name=COLLECTION_NAME,
            wait=True,
            points=points # The fix is passing the list directly
        )
        print("\n--- Ingestion Complete ---")
        print(f"Status: {operation_info.status.name}")
        print(f"Points inserted/updated: {len(points)}")
        
    except Exception as e:
        print(f"Error during upsert: {e}")

if __name__ == "__main__":
    ingest_data()