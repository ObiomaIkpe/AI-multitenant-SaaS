from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from ..models.enums import DocumentStatus


# ---------------------------------------
# Request Schema: Upload Document
# ---------------------------------------
class DocumentUploadRequest(BaseModel):
    filename: str
    file_size: int
    file_type: str

    # Optional metadata
    category: Optional[str] = None
    tags: List[str] = []
    description: Optional[str] = None


# ---------------------------------------
# Response Schema: After Upload
# ---------------------------------------
class DocumentUploadResponse(BaseModel):
    status: str
    document_id: str
    filename: str
    file_size: int
    chunks_created: int
    metadata: dict


# ---------------------------------------
# Request Schema: Update Document Metadata
# ---------------------------------------
class DocumentUpdateRequest(BaseModel):
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    description: Optional[str] = None


# ---------------------------------------
# Response Schema: A Single Document
# ---------------------------------------
class DocumentResponse(BaseModel):
    id: str
    tenant_id: str
    filename: str
    file_size: int
    file_type: str

    status: DocumentStatus
    chunk_count: int
    error_message: Optional[str]
    processed_at: Optional[datetime]

    category: Optional[str]
    tags: List[str]
    description: Optional[str]

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # replaces orm_mode=True in Pydantic v2


# ---------------------------------------
# Response Schema: List of Documents
# ---------------------------------------
class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
