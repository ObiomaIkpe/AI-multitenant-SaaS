from qdrant_client import QdrantClient, models
import os

# Configuration (Use localhost because you ran Qdrant locally via Docker)
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "enterprise_knowledge"
# You MUST match the vector size to your embedding model (e.g., 1536 for OpenAI, 384 for sentence-transformers)
VECTOR_DIMENSION=384 

def create_collection_with_index():
    # Initialize the client (using the standard sync client for this setup script)
    client = QdrantClient(url=QDRANT_URL)

    # 1. Define Vector Configuration (Size and Distance)
    vectors_config = models.VectorParams(
        size=VECTOR_DIMENSION, 
        distance=models.Distance.COSINE # COSINE is standard for text embeddings
    )

    # 2. Create the Collection
    print(f"Creating collection '{COLLECTION_NAME}'...")
    try:
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=vectors_config,
        )
        print(f"Collection '{COLLECTION_NAME}' created successfully.")
    except Exception as e:
        print(f"Error creating collection: {e}")
        return

    # 3. Create the CRITICAL Payload Index for Multi-Tenancy
    # This optimizes the search speed when filtering by 'tenant_id'
    # 3. Create the CRITICAL Payload Index for Multi-Tenancy
    TENANT_FIELD_NAME = "tenant_id"
    
    print(f"Creating payload index on '{TENANT_FIELD_NAME}'...")
    try:
        # **CORRECTED SYNTAX:** Pass KeywordIndexParams directly to field_schema
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name=TENANT_FIELD_NAME,
            # Use KeywordIndexParams to specify the type and the crucial is_tenant=True flag
            field_schema=models.KeywordIndexParams(
                type=models.PayloadSchemaType.KEYWORD,
                is_tenant=True # This flag optimizes storage for multi-tenancy
            ),
        )
        print(f"Payload index for '{TENANT_FIELD_NAME}' created successfully. Multi-Tenancy ready.")
    except Exception as e:
        print(f"Error creating payload index: {e}")
        
    print("\n--- Setup Complete ---")

if __name__ == "__main__":
    create_collection_with_index()