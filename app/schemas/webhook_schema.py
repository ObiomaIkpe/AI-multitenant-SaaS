from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime

class WebhookCreate(BaseModel):
    url: HttpUrl
    events: List[str]  # e.g., ["document.uploaded", "quota.reached"]

class WebhookResponse(BaseModel):
    id: str
    tenant_id: str
    url: str
    events: List[str]
    is_active: bool
    total_deliveries: int
    failed_deliveries: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class WebhookUpdate(BaseModel):
    url: Optional[HttpUrl] = None
    events: Optional[List[str]] = None
    is_active: Optional[bool] = None