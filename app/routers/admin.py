from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.document import Tenant, User, Document
from app.schemas.admin_schema import (
    TenantCreate,
    TenantResponse,
    TenantListResponse,
    TenantStatsResponse
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/tenants", response_model=TenantListResponse)
async def list_tenants(
    db: AsyncSession = Depends(get_db)
):
    """List all tenants in the system."""
    result = await db.execute(select(Tenant))
    tenants = result.scalars.all()

    tenant_responses = []
    for tenant in tenants:
        owner_result = await db.execute(select(User).where(User.id == tenant.owner_id))
        owner = owner_result.scalar_one_or_none()

        tenant_responses.append(TenantResponse(
            id=tenant.id,
            name=tenant.name,
            owner_id=tenant.owner_id,
            owner_email=owner.email if owner else "N/A",
            max_documents = tenants.max_documents,
            max_queries_per_day=tenant.max_queries_per_day,
            created_at=tenant.created_at
        ))

        return TenantListResponse(total=len(tenant_responses), tenants=tenant_responses)
    


@router.get("tenants/{tenant_id}/stats", response_model=TenantStatsResponse)
async def get_tenant_stats(tenant_id: str, db: AsyncSession = Depends(get_db)):
    """Get usage stats for a tenant."""
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(status_code=404, message="Tenant not found")
    
    doc_result = await db.execute(select(func.count()).select_from(Document).where(Document.tenant_id == tenant_id))
    doc_count = doc_result.scalar()
    
    # Calculate storage
    size_result = await db.execute(select(func.sum(Document.file_size)).where(Document.tenant_id == tenant_id))
    total_bytes = size_result.scalar() or 0
    storage_mb = total_bytes / (1024 * 1024)
    
    return TenantStatsResponse(
        tenant_id=tenant.id,
        tenant_name=tenant.name,
        document_count=doc_count,
        total_queries=0,  # TODO: Implement query logging
        storage_used_mb=round(storage_mb, 2)
    )


# 3. Create new tenant
# @router.post("/tenants", response_model=TenantResponse)
# async def create_tenant(
#     tenant_data: TenantCreate,
#     db: AsyncSession = Depends(get_db)
# ):
#     """Create a new tenant with owner user"""
#     from app.core.security import get_password_hash
#     import uuid
    
#     # Check if email exists
#     result = await db.execute(select(User).where(User.email == tenant_data.owner_email))
#     if result.scalar_one_or_none():
#         raise HTTPException(status_code=400, detail="Email already registered")
    
#     # Create user
#     user = User(
#         id=f"user_{uuid.uuid4().hex[:12]}",
#         email=tenant_data.owner_email,
#         hashed_password=get_password_hash(tenant_data.owner_password),
#         is_active=True
#     )
#     db.add(user)
#     await db.flush()
    
    
#     tenant = Tenant(
#         id=f"tenant_{uuid.uuid4().hex[:12]}",
#         name=tenant_data.name,
#         owner_id=user.id,
#         max_documents=tenant_data.max_documents,
#         max_queries_per_day=tenant_data.max_queries_per_day
#     )
#     db.add(tenant)
#     await db.commit()
#     await db.refresh(tenant)
    
#     return TenantResponse(
#         id=tenant.id,
#         name=tenant.name,
#         owner_id=tenant.owner_id,
#         owner_email=user.email,
#         max_documents=tenant.max_documents,
#         max_queries_per_day=tenant.max_queries_per_day,
#         created_at=tenant.created_at
#     )


@router.delete("/tenants/{tenant_id}")
async def delete_tenant(
    tenant_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a tenant and all associated data"""
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    await db.delete(tenant)
    await db.commit()
    
    return {"status": "success", "message": f"Tenant {tenant_id} deleted"}

from app.models.document import QueryLog

# Get query analytics
@router.get("/analytics/queries")
async def get_query_analytics(
    tenant_id: Optional[str] = None,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Get query analytics (optionally filtered by tenant)"""
    from datetime import timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Build query
    stmt = select(QueryLog).where(QueryLog.created_at >= cutoff_date)
    if tenant_id:
        stmt = stmt.where(QueryLog.tenant_id == tenant_id)
    
    result = await db.execute(stmt)
    logs = result.scalars().all()
    
    # Calculate stats
    total_queries = len(logs)
    successful_queries = sum(1 for log in logs if log.success)
    failed_queries = total_queries - successful_queries
    avg_response_time = sum(log.response_time_ms for log in logs if log.response_time_ms) / total_queries if total_queries > 0 else 0
    
    return {
        "period_days": days,
        "total_queries": total_queries,
        "successful_queries": successful_queries,
        "failed_queries": failed_queries,
        "success_rate": round(successful_queries / total_queries * 100, 2) if total_queries > 0 else 0,
        "avg_response_time_ms": round(avg_response_time, 2)
    }


# Get queries over time
@router.get("/analytics/queries-over-time")
async def get_queries_over_time(
    tenant_id: Optional[str] = None,
    days: int = 7,
    db: AsyncSession = Depends(get_db)
):
    """Get query count grouped by date"""
    from datetime import timedelta
    from collections import defaultdict
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    stmt = select(QueryLog).where(QueryLog.created_at >= cutoff_date)
    if tenant_id:
        stmt = stmt.where(QueryLog.tenant_id == tenant_id)
    
    result = await db.execute(stmt)
    logs = result.scalars().all()
    
    # Group by date
    queries_by_date = defaultdict(int)
    for log in logs:
        date_key = log.created_at.date().isoformat()
        queries_by_date[date_key] += 1
    
    return {
        "period_days": days,
        "data": [{"date": date, "count": count} for date, count in sorted(queries_by_date.items())]
    }


# Get popular documents
@router.get("/analytics/popular-documents")
async def get_popular_documents(
    tenant_id: Optional[str] = None,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get most queried documents"""
    from collections import Counter
    
    stmt = select(QueryLog)
    if tenant_id:
        stmt = stmt.where(QueryLog.tenant_id == tenant_id)
    
    result = await db.execute(stmt)
    logs = result.scalars().all()
    
    # Count document mentions in filters
    doc_counter = Counter()
    for log in logs:
        filters = log.filters_applied or {}
        if "document_ids" in filters:
            for doc_id in filters["document_ids"]:
                doc_counter[doc_id] += 1
    
    return {
        "popular_documents": [
            {"document_id": doc_id, "query_count": count}
            for doc_id, count in doc_counter.most_common(limit)
        ]
    }