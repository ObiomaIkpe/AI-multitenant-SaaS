from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import secrets

from app.database import get_db
from app.core.security import get_current_tenant_id
from app.models.document import Webhook
from app.schemas.webhook_schema import WebhookCreate, WebhookResponse, WebhookUpdate

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@router.post("/", response_model=WebhookResponse)
async def create_webhook(
    webhook_data: WebhookCreate,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """Create a new webhook"""
    webhook = Webhook(
        tenant_id=tenant_id,
        url=str(webhook_data.url),
        events=webhook_data.events,
        secret=secrets.token_urlsafe(32)  # Generate random secret
    )
    
    db.add(webhook)
    await db.commit()
    await db.refresh(webhook)
    
    return webhook


@router.get("/", response_model=List[WebhookResponse])
async def list_webhooks(
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """List all webhooks for current tenant"""
    result = await db.execute(
        select(Webhook).where(Webhook.tenant_id == tenant_id)
    )
    webhooks = result.scalars().all()
    return webhooks


@router.get("/{webhook_id}", response_model=WebhookResponse)
async def get_webhook(
    webhook_id: str,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """Get webhook details"""
    result = await db.execute(
        select(Webhook).where(
            Webhook.id == webhook_id,
            Webhook.tenant_id == tenant_id
        )
    )
    webhook = result.scalar_one_or_none()
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    return webhook


@router.patch("/{webhook_id}", response_model=WebhookResponse)
async def update_webhook(
    webhook_id: str,
    update_data: WebhookUpdate,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """Update webhook configuration"""
    result = await db.execute(
        select(Webhook).where(
            Webhook.id == webhook_id,
            Webhook.tenant_id == tenant_id
        )
    )
    webhook = result.scalar_one_or_none()
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    if update_data.url is not None:
        webhook.url = str(update_data.url)
    if update_data.events is not None:
        webhook.events = update_data.events
    if update_data.is_active is not None:
        webhook.is_active = update_data.is_active
    
    await db.commit()
    await db.refresh(webhook)
    
    return webhook


@router.delete("/{webhook_id}")
async def delete_webhook(
    webhook_id: str,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """Delete a webhook"""
    result = await db.execute(
        select(Webhook).where(
            Webhook.id == webhook_id,
            Webhook.tenant_id == tenant_id
        )
    )
    webhook = result.scalar_one_or_none()
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    await db.delete(webhook)
    await db.commit()
    
    return {"status": "success", "message": "Webhook deleted"}


@router.post("/{webhook_id}/test")
async def test_webhook(
    webhook_id: str,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """Send a test webhook"""
    from app.utils.webhooks import trigger_webhook
    
    result = await db.execute(
        select(Webhook).where(
            Webhook.id == webhook_id,
            Webhook.tenant_id == tenant_id
        )
    )
    webhook = result.scalar_one_or_none()
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    # Send test event
    await trigger_webhook(
        db=db,
        tenant_id=tenant_id,
        event="test.webhook",
        payload={"message": "This is a test webhook"}
    )
    
    return {"status": "success", "message": "Test webhook sent"}