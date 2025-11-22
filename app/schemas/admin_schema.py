from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class TenantCreate(BaseModel):
    name: str
    owner_email: EmailStr
    owner_password: str
    max_documents: int = 100
    max_queries_per_day: int = 100

class TenantResponse(BaseModel):
    id: str
    name: str
    owner_id: str
    owner_email: str
    max_documents: int
    max_queries_per_day: int
    created_at: datetime

    class Config:
        from_attributes = True

class TenantListResponse(BaseModel):
    total: int
    tenants: List[TenantResponse]

class TenantStatsResponse(BaseModel):
    tenant_id: str
    tenant_name: str
    document_count: str
    total_queries: int
    storage_used_mb: float