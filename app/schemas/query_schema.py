from pydantic import BaseModel, Field
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str = Field(..., description="The natural language question")
    
    # NEW: Optional filters
    document_ids: Optional[List[str]] = Field(
        None, 
        description="Filter by specific document IDs",
        example=["doc_abc123", "doc_xyz789"]
    )
    categories: Optional[List[str]] = Field(
        None,
        description="Filter by document categories",
        example=["programming", "machine-learning"]
    )
    tags: Optional[List[str]] = Field(
        None,
        description="Filter by document tags",
        example=["python", "tutorial"]
    )
    file_types: Optional[List[str]] = Field(
        None,
        description="Filter by file types",
        example=["pdf", "txt"]
    )
    date_from: Optional[str] = Field(
        None,
        description="Filter documents uploaded after this date",
        example="2025-01-01T00:00:00"
    )
    date_to: Optional[str] = Field(
        None,
        description="Filter documents uploaded before this date",
        example="2025-12-31T23:59:59"
    )

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]  # Changed from List[str] to include metadata
    filters_applied: dict  # NEW: Show what filters were used